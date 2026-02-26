"""Word lookup and dictionary endpoints for Learning Finnish API"""

import json
import logging
import uuid
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models_db import Word, UserWord, User, WordStatusEnum
from app.models import (
    Word as WordSchema,
    WordSearchResult,
    UserWord as UserWordSchema,
    SaveWordRequest,
    UpdateWordStatusRequest,
    AIDefinitionRequest,
    GrammaticalForm,
    ExampleSentence,
)
from app.services.ai_service import ai_service
from app.services.inflection_service import (
    generate_and_store_inflections,
    generate_batch_inflections,
    normalize_word,
    normalize_word_batch,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/words", tags=["words"])


def _word_to_schema(word_db: Word) -> WordSchema:
    """Convert database Word model to Pydantic schema"""
    grammatical_forms = None
    if word_db.grammatical_forms:
        try:
            forms_data = json.loads(word_db.grammatical_forms)
            grammatical_forms = [GrammaticalForm(**form) for form in forms_data]
        except (json.JSONDecodeError, TypeError):
            pass

    example_sentences = None
    if word_db.example_sentences:
        try:
            sentences_data = json.loads(word_db.example_sentences)
            example_sentences = [ExampleSentence(**sent) for sent in sentences_data]
        except (json.JSONDecodeError, TypeError):
            pass

    ai_examples = None
    if word_db.ai_examples:
        try:
            examples_data = json.loads(word_db.ai_examples)
            ai_examples = [ExampleSentence(**ex) for ex in examples_data]
        except (json.JSONDecodeError, TypeError):
            pass

    return WordSchema(
        id=word_db.id,
        finnish_word=word_db.finnish_word,
        english_translation=word_db.english_translation,
        part_of_speech=word_db.part_of_speech,
        grammatical_forms=grammatical_forms,
        example_sentences=example_sentences,
        ai_definition=word_db.ai_definition,
        ai_examples=ai_examples,
        created_at=word_db.created_at,
        updated_at=word_db.updated_at,
    )


@router.get("")
async def list_words(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    word_type: Optional[str] = Query(None, description="Filter by part_of_speech"),
    search: Optional[str] = Query(None, description="Search finnish/danish/english"),
    db: AsyncSession = Depends(get_db),
):
    """List vocabulary words (spaced repetition) with optional filters."""
    stmt = select(Word).order_by(Word.priority.desc(), Word.finnish_word)
    if word_type:
        stmt = stmt.where(Word.part_of_speech.ilike(word_type))
    if search and search.strip():
        q = f"%{search.strip()}%"
        from sqlalchemy import or_
        stmt = stmt.where(
            or_(
                Word.finnish_word.ilike(q),
                Word.english_translation.ilike(q),
                Word.danish_translation.ilike(q),
            )
        )
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    words = result.scalars().all()
    return [
        {
            "id": w.id,
            "finnish": w.finnish_word,
            "danish": w.danish_translation,
            "english": w.english_translation,
            "word_type": w.part_of_speech,
            "priority": w.priority,
            "times_served": w.times_served,
            "last_score": w.last_score,
        }
        for w in words
    ]


@router.post("/search", response_model=WordSearchResult)
async def search_word(
    finnish_word: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
) -> WordSearchResult:
    """
    Search for a Finnish word and return translation with metadata

    Args:
        finnish_word: The Finnish word to search for
        db: Database session

    Returns:
        WordSearchResult with word information
    """
    logger.info(f"Searching for word: {finnish_word}")

    # Try to query database, fall back to mock data if unavailable
    word_db = None
    try:
        stmt = select(Word).where(Word.finnish_word.ilike(finnish_word))
        result = await db.execute(stmt)
        word_db = result.scalars().first()
    except Exception as db_error:
        logger.warning(f"Database query failed: {db_error}, using mock data")

    if word_db:
        word_schema = _word_to_schema(word_db)
        return WordSearchResult(
            id=word_schema.id,
            finnish_word=word_schema.finnish_word,
            english_translation=word_schema.english_translation,
            part_of_speech=word_schema.part_of_speech,
            grammatical_forms=word_schema.grammatical_forms,
            example_sentences=word_schema.example_sentences,
            ai_definition=word_schema.ai_definition,
        )

    # Return mock data for demonstration
    logger.info(f"Returning mock data for word: {finnish_word}")
    return WordSearchResult(
        finnish_word=finnish_word,
        english_translation=_get_mock_translation(finnish_word),
        part_of_speech=_get_mock_part_of_speech(finnish_word),
        grammatical_forms=await ai_service.get_grammatical_forms(finnish_word),
        example_sentences=await ai_service.get_example_sentences(finnish_word),
        ai_definition=await ai_service.get_word_definition(finnish_word),
    )


@router.post("/bulk-add")
async def bulk_add_words(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk add words. Supports multiple input formats:

    Fully specified (skip normalization):
      {"rows": [["finnish", "danish", "english", "word_type"], ...]}
      {"csv": "finnish,danish,english,word_type\\ntalo,hus,house,noun\\n..."}

    Words only (LLM normalizes — any language):
      {"words": ["hus", "to run", "juosta", "kaunis"]}
      Optional: {"words": [...], "source_lang": "da"}
    """
    # --- New: simple word list (any language) ---
    word_list = request.get("words")
    if word_list and isinstance(word_list, list):
        source_lang = request.get("source_lang")
        inputs = [{"text": str(w).strip(), "source_lang": source_lang} for w in word_list if str(w).strip()]
        if not inputs:
            raise HTTPException(status_code=400, detail="No valid words provided")

        norms = await normalize_word_batch(inputs)

        created = 0
        exists = 0
        invalid = []
        new_words = []

        for inp, norm in zip(inputs, norms):
            if not norm.get("valid"):
                invalid.append({"input": inp["text"], "error": norm.get("error")})
                continue

            finnish = norm["finnish"]
            stmt = select(Word).where(Word.finnish_word.ilike(finnish))
            result = await db.execute(stmt)
            existing = result.scalars().first()
            if existing:
                exists += 1
                continue

            word = Word(
                id=str(uuid.uuid4()),
                finnish_word=finnish,
                danish_translation=norm.get("danish"),
                english_translation=norm.get("english") or finnish,
                part_of_speech=norm.get("word_type", "noun"),
                tags=json.dumps([]),
                priority=1.0,
            )
            db.add(word)
            await db.flush()
            new_words.append(word)
            created += 1

        inflection_result = {"inflections": 0, "verb_forms": 0, "skipped": 0}
        if new_words:
            inflection_result = await generate_batch_inflections(db, new_words)

        await db.commit()
        return {
            "created": created,
            "exists": exists,
            "invalid": invalid[:20],
            "inflections_generated": inflection_result,
        }

    # --- Legacy: CSV/rows format (assumed Finnish with all fields) ---
    rows = request.get("rows")
    if not rows and "csv" in request:
        import csv
        import io
        csv_text = request["csv"]
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
    if not rows or not isinstance(rows, list):
        raise HTTPException(status_code=400, detail="Provide 'words' list, 'rows' array, or 'csv' string")

    # Check if rows lack word_type — if so, normalize to get types
    needs_normalize = any(
        len(row) < 4 or not (row[3] or "").strip()
        for row in rows
        if row and isinstance(row, (list, tuple)) and len(row) > 0 and (row[0] or "").strip()
    )

    if needs_normalize:
        inputs = []
        for row in rows:
            if not row or not isinstance(row, (list, tuple)):
                continue
            text = (row[0] or "").strip() if len(row) > 0 else ""
            if text:
                inputs.append({"text": text, "source_lang": "fi"})
        if inputs:
            norms = await normalize_word_batch(inputs)
            norm_map = {n["finnish"].lower(): n for n in norms if n.get("valid") and n.get("finnish")}
        else:
            norm_map = {}
    else:
        norm_map = {}

    created = 0
    exists = 0
    errors = []
    new_words = []

    for i, row in enumerate(rows):
        if not row or not isinstance(row, (list, tuple)):
            continue
        finnish = (row[0] or "").strip() if len(row) > 0 else ""
        if not finnish:
            continue
        danish = (row[1] or "").strip() if len(row) > 1 else None
        english = (row[2] or "").strip() if len(row) > 2 else finnish
        word_type = (row[3] or "").strip().lower() if len(row) > 3 else ""

        # Fill missing fields from normalization
        if not word_type and norm_map:
            norm = norm_map.get(finnish.lower(), {})
            word_type = norm.get("word_type", "noun")
            if not danish:
                danish = norm.get("danish")
            if not english or english == finnish:
                english = norm.get("english", finnish)

        word_type = word_type or "noun"

        try:
            stmt = select(Word).where(Word.finnish_word.ilike(finnish))
            result = await db.execute(stmt)
            existing = result.scalars().first()
            if existing:
                exists += 1
                continue
            word = Word(
                id=str(uuid.uuid4()),
                finnish_word=finnish,
                danish_translation=danish,
                english_translation=english,
                part_of_speech=word_type,
                tags=json.dumps([]),
                priority=1.0,
            )
            db.add(word)
            await db.flush()
            new_words.append(word)
            created += 1
        except Exception as e:
            errors.append({"row": i + 1, "word": finnish, "error": str(e)})

    # Batch generate inflections in grouped LLM calls instead of one per word
    inflection_result = {"inflections": 0, "verb_forms": 0, "skipped": 0}
    if new_words:
        inflection_result = await generate_batch_inflections(db, new_words)

    await db.commit()
    return {
        "created": created,
        "exists": exists,
        "errors": errors[:20],
        "inflections_generated": inflection_result,
    }


async def _add_word_impl(request: dict, db: AsyncSession):
    """
    Shared implementation for POST /words and POST /words/add.

    Accepts input in Finnish, Danish, or English. The LLM normalizes:
    - Detects language and translates to Finnish if needed
    - Corrects spelling and finds the base form (lemma)
    - Identifies word type automatically

    Body: {"word": "hus"} or {"finnish": "talo", "danish": "hus", ...}
    Optional: "source_lang": "da"|"en"|"fi" as a hint
    """
    # Support both "word" (new: any language) and "finnish" (legacy: assumed Finnish)
    input_text = (request.get("word") or request.get("finnish") or "").strip()
    if not input_text:
        raise HTTPException(status_code=400, detail="'word' or 'finnish' is required")

    source_lang = request.get("source_lang")

    # If caller already provided finnish + word_type, skip normalization
    has_finnish = bool(request.get("finnish"))
    has_word_type = bool(request.get("word_type"))
    skip_normalize = has_finnish and has_word_type

    if skip_normalize:
        finnish = request["finnish"].strip()
        danish = request.get("danish")
        english = request.get("english", finnish)
        word_type = request["word_type"]
        norm_info = None
    else:
        norm = await normalize_word(input_text, source_lang)
        if not norm.get("valid"):
            return {
                "status": "invalid",
                "error": norm.get("error", "Word not recognized"),
                "input": input_text,
                "normalization": norm,
            }
        finnish = norm["finnish"]
        danish = norm.get("danish")
        english = norm.get("english", finnish)
        word_type = norm.get("word_type", "noun")
        norm_info = {
            "detected_lang": norm.get("detected_lang"),
            "was_corrected": norm.get("was_corrected"),
            "correction_note": norm.get("correction_note"),
        }

    # Check for duplicates
    stmt = select(Word).where(Word.finnish_word.ilike(finnish))
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        resp = {"status": "exists", "word_id": existing.id, "finnish": existing.finnish_word}
        if norm_info:
            resp["normalization"] = norm_info
        return resp

    word = Word(
        id=str(uuid.uuid4()),
        finnish_word=finnish,
        danish_translation=danish,
        english_translation=english or finnish,
        part_of_speech=word_type,
        tags=json.dumps(request.get("tags", [])),
        priority=1.0,
    )
    db.add(word)
    await db.flush()

    infl_result = await generate_and_store_inflections(db, word)
    await db.commit()

    resp = {
        "status": "created",
        "word_id": word.id,
        "finnish": word.finnish_word,
        "danish": danish,
        "english": english,
        "word_type": word_type,
        "inflections_generated": infl_result,
    }
    if norm_info:
        resp["normalization"] = norm_info
    return resp


@router.post("")
@router.post("/add")
async def add_word_simple(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Add word (OpenClaw). Accepts both POST /api/words and POST /api/words/add.
    Body: {"finnish": "talo", "danish": "hus", "english": "house", "word_type": "noun"}
    """
    return await _add_word_impl(request, db)


@router.post("/save", response_model=UserWordSchema)
async def save_word(
    request: SaveWordRequest,
    db: AsyncSession = Depends(get_db),
) -> UserWordSchema:
    """
    Save a word to user's wordbook

    Args:
        request: SaveWordRequest with user_id and finnish_word
        db: Database session

    Returns:
        UserWordSchema with the saved word
    """
    logger.info(f"User {request.user_id} saving word: {request.finnish_word}")

    try:
        # Verify user exists or create if not
        user_stmt = select(User).where(User.id == request.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalars().first()

        if not user:
            # Create user if doesn't exist (for demo purposes)
            user = User(id=request.user_id, username=f"user_{request.user_id}")
            db.add(user)
            await db.flush()
            logger.info(f"Created new user: {request.user_id}")
    except Exception as e:
        logger.warning(f"Could not verify/create user: {e}, continuing with word save")
        # Continue anyway - some endpoints might work even if user check fails

    try:
        # Check if word exists in database
        word_stmt = select(Word).where(Word.finnish_word.ilike(request.finnish_word))
        word_result = await db.execute(word_stmt)
        word_db = word_result.scalars().first()

        # Create word if it doesn't exist
        if not word_db:
            word_db = Word(
                id=str(uuid.uuid4()),
                finnish_word=request.finnish_word,
                english_translation=_get_mock_translation(request.finnish_word),
                part_of_speech=_get_mock_part_of_speech(request.finnish_word),
                grammatical_forms=json.dumps(
                    [
                        form.model_dump()
                        for form in (await ai_service.get_grammatical_forms(request.finnish_word) or [])
                    ]
                ),
                example_sentences=json.dumps(
                    [
                        sent.model_dump()
                        for sent in (await ai_service.get_example_sentences(request.finnish_word) or [])
                    ]
                ),
                ai_definition=await ai_service.get_word_definition(request.finnish_word),
                priority=1.0,
            )
            db.add(word_db)
            await db.flush()
            inflection_result = await generate_and_store_inflections(db, word_db)
            logger.info(f"Generated inflections for '{word_db.finnish_word}': {inflection_result}")

        # Check if user already has this word
        user_word_stmt = select(UserWord).where(
            (UserWord.user_id == request.user_id) & (UserWord.word_id == word_db.id)
        )
        user_word_result = await db.execute(user_word_stmt)
        user_word = user_word_result.scalars().first()

        if user_word:
            logger.info(f"Word {word_db.id} already in user {request.user_id}'s wordbook")
            return UserWordSchema(
                id=user_word.id,
                user_id=user_word.user_id,
                word_id=user_word.word_id,
                word=_word_to_schema(word_db),
                status=user_word.status.value,
                proficiency=user_word.proficiency,
                date_added=user_word.date_added,
                last_reviewed=user_word.last_reviewed,
                review_count=user_word.review_count,
            )

        # Create new user word entry
        user_word = UserWord(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            word_id=word_db.id,
            status=WordStatusEnum.RECENT,
            proficiency=0,
        )
        db.add(user_word)
        await db.commit()
        await db.refresh(user_word)

        return UserWordSchema(
            id=user_word.id,
            user_id=user_word.user_id,
            word_id=user_word.word_id,
            word=_word_to_schema(word_db),
            status=user_word.status.value,
            proficiency=user_word.proficiency,
            date_added=user_word.date_added,
            review_count=user_word.review_count,
        )
    except Exception as e:
        logger.error(f"Error saving word: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving word: {str(e)}")


@router.get("/user-words/{user_id}", response_model=List[UserWordSchema])
async def get_user_words(
    user_id: str,
    status: Optional[str] = Query(None, description="Filter by status: recent, learning, mastered"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[UserWordSchema]:
    """
    Get user's saved words with their learning status

    Args:
        user_id: The user ID
        status: Optional status filter
        limit: Number of results to return
        offset: Number of results to skip
        db: Database session

    Returns:
        List of UserWordSchema objects
    """
    logger.info(f"Fetching words for user {user_id}")

    try:
        # Verify user exists or create if not
        user_stmt = select(User).where(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalars().first()

        if not user:
            # Create user if doesn't exist (for demo purposes)
            user = User(id=user_id, username=f"user_{user_id}")
            db.add(user)
            await db.flush()
            logger.info(f"Created new user: {user_id}")

        # Build query
        stmt = select(UserWord).where(UserWord.user_id == user_id)

        if status:
            try:
                status_enum = WordStatusEnum(status.lower())
                stmt = stmt.where(UserWord.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: recent, learning, mastered"
                )

        stmt = stmt.options(selectinload(UserWord.word)).limit(limit).offset(offset)
        result = await db.execute(stmt)
        user_words = result.scalars().unique().all()

        return [
            UserWordSchema(
                id=uw.id,
                user_id=uw.user_id,
                word_id=uw.word_id,
                word=_word_to_schema(uw.word) if uw.word else None,
                status=uw.status.value,
                proficiency=uw.proficiency,
                date_added=uw.date_added,
                last_reviewed=uw.last_reviewed,
                review_count=uw.review_count,
            )
            for uw in user_words
        ]
    except Exception as e:
        logger.error(f"Error fetching user words: {e}")
        # Return empty list on error instead of failing
        return []


@router.put("/{word_id}/status/{user_id}", response_model=UserWordSchema)
async def update_word_status(
    word_id: str,
    user_id: str,
    request: UpdateWordStatusRequest,
    db: AsyncSession = Depends(get_db),
) -> UserWordSchema:
    """
    Update word status and proficiency for a user

    Args:
        word_id: The word ID
        user_id: The user ID
        request: UpdateWordStatusRequest with new status and optional proficiency
        db: Database session

    Returns:
        Updated UserWordSchema
    """
    logger.info(f"Updating word {word_id} status for user {user_id}")

    # Get user word
    stmt = select(UserWord).where(
        (UserWord.user_id == user_id) & (UserWord.word_id == word_id)
    ).options(selectinload(UserWord.word))
    result = await db.execute(stmt)
    user_word = result.scalars().first()

    if not user_word:
        raise HTTPException(status_code=404, detail="Word not found in user's wordbook")

    # Update status
    user_word.status = WordStatusEnum(request.status.value)

    # Update proficiency if provided
    if request.proficiency is not None:
        user_word.proficiency = max(0, min(100, request.proficiency))

    # Update review tracking
    user_word.last_reviewed = datetime.utcnow()
    user_word.review_count += 1
    user_word.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user_word)

    return UserWordSchema(
        id=user_word.id,
        user_id=user_word.user_id,
        word_id=user_word.word_id,
        word=_word_to_schema(user_word.word) if user_word.word else None,
        status=user_word.status.value,
        proficiency=user_word.proficiency,
        date_added=user_word.date_added,
        last_reviewed=user_word.last_reviewed,
        review_count=user_word.review_count,
    )


@router.get("/{word_id}/ai-definition", response_model=dict)
async def get_ai_definition(
    word_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get AI-powered definition for a word

    Args:
        word_id: The word ID
        db: Database session

    Returns:
        Dictionary with definition and examples
    """
    logger.info(f"Getting AI definition for word {word_id}")

    # Get word from database
    stmt = select(Word).where(Word.id == word_id)
    result = await db.execute(stmt)
    word_db = result.scalars().first()

    if not word_db:
        raise HTTPException(status_code=404, detail="Word not found")

    # If AI definition doesn't exist, generate it
    if not word_db.ai_definition:
        word_db.ai_definition = await ai_service.get_word_definition(word_db.finnish_word)
        await db.commit()

    # If AI examples don't exist, generate them
    if not word_db.ai_examples:
        examples = await ai_service.get_example_sentences(word_db.finnish_word)
        if examples:
            word_db.ai_examples = json.dumps([ex.model_dump() for ex in examples])
            await db.commit()

    ai_examples = []
    if word_db.ai_examples:
        try:
            ai_examples = json.loads(word_db.ai_examples)
        except json.JSONDecodeError:
            pass

    return {
        "word_id": word_db.id,
        "finnish_word": word_db.finnish_word,
        "ai_definition": word_db.ai_definition,
        "ai_examples": ai_examples,
    }


@router.get("/{word_id}/inflections")
async def get_word_inflections(
    word_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all inflections/verb forms for a word."""
    stmt = (
        select(Word)
        .where(Word.id == word_id)
        .options(selectinload(Word.inflections), selectinload(Word.verb_forms))
    )
    result = await db.execute(stmt)
    word = result.scalars().first()

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    return {
        "word_id": word.id,
        "finnish_word": word.finnish_word,
        "part_of_speech": word.part_of_speech,
        "inflections": [
            {"case_name": i.case_name, "degree": i.degree, "singular": i.singular, "plural": i.plural, "notes": i.notes}
            for i in (word.inflections or [])
        ],
        "verb_forms": [
            {"form_name": v.form_name, "form_value": v.form_value, "tense": v.tense, "notes": v.notes}
            for v in (word.verb_forms or [])
        ],
    }


@router.post("/{word_id}/inflections/generate")
async def regenerate_inflections(
    word_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Re-generate inflections for a word using the LLM."""
    from sqlalchemy import delete
    from app.models_db import Inflection, VerbForm

    stmt = select(Word).where(Word.id == word_id)
    result = await db.execute(stmt)
    word = result.scalars().first()

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    await db.execute(delete(Inflection).where(Inflection.word_id == word_id))
    await db.execute(delete(VerbForm).where(VerbForm.word_id == word_id))
    await db.commit()

    inflection_result = await generate_and_store_inflections(db, word)
    return {"status": "ok", **inflection_result}


@router.delete("/{word_id}/{user_id}", response_model=dict)
async def remove_word_from_wordbook(
    word_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Remove a word from user's wordbook

    Args:
        word_id: The word ID
        user_id: The user ID
        db: Database session

    Returns:
        Success message
    """
    logger.info(f"Removing word {word_id} from user {user_id}'s wordbook")

    # Get user word
    stmt = select(UserWord).where(
        (UserWord.user_id == user_id) & (UserWord.word_id == word_id)
    )
    result = await db.execute(stmt)
    user_word = result.scalars().first()

    if not user_word:
        raise HTTPException(status_code=404, detail="Word not found in user's wordbook")

    await db.delete(user_word)
    await db.commit()

    return {"status": "success", "message": "Word removed from wordbook"}


# Mock data helper functions
def _get_mock_translation(finnish_word: str) -> str:
    """Get mock English translation"""
    mock_translations = {
        "kissa": "cat",
        "koulu": "school",
        "kirja": "book",
        "ystävä": "friend",
        "kauneus": "beauty",
        "mies": "man",
        "nainen": "woman",
        "talo": "house",
        "vesi": "water",
        "puu": "tree",
        "auto": "car",
        "lintú": "bird",
        "kala": "fish",
        "kukka": "flower",
        "sää": "weather",
    }
    return mock_translations.get(finnish_word.lower(), finnish_word)


def _get_mock_part_of_speech(finnish_word: str) -> str:
    """Get mock part of speech"""
    mock_pos = {
        "kissa": "noun",
        "koulu": "noun",
        "kirja": "noun",
        "ystävä": "noun",
        "kauneus": "noun",
        "mies": "noun",
        "nainen": "noun",
        "talo": "noun",
        "vesi": "noun",
        "puu": "noun",
    }
    return mock_pos.get(finnish_word.lower(), "noun")
