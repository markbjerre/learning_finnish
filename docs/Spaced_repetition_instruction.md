# Finnish Learning — Spaced Repetition Engine

**For:** Cursor Agent
**Date:** February 19, 2026
**Prerequisite:** DB running on homelab via Tailscale, existing FastAPI backend in `backend/`
**Goal:** Extend the existing FastAPI backend with spaced repetition logic, inflection storage, and exercise endpoints for OpenClaw integration.

---

## Context: What Already Exists

The project has a working FastAPI backend with these key files:

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app, mounts routers at `/api` |
| `backend/app/database.py` | Async SQLAlchemy engine, uses `app` schema in PostgreSQL |
| `backend/app/config.py` | Pydantic settings from `.env` |
| `backend/app/models_db.py` | SQLAlchemy ORM models |
| `backend/app/models/__init__.py` | Pydantic request/response schemas |
| `backend/app/routers/words.py` | Word CRUD + search + AI definitions |
| `backend/app/services/ai_service.py` | OpenAI integration with mock fallback |

### Existing DB Models (in `app` schema)

- `Word` — dictionary entries (String PKs, `finnish_word`, `english_translation`, `part_of_speech`, JSON `grammatical_forms`, `example_sentences`, `ai_definition`)
- `UserWord` — user ↔ word link with `status` (recent/learning/mastered), `proficiency` (0-100), `review_count`
- `User`, `Lesson`, `VocabularyList`, `VocabularyWord`, `Exercise`, `LessonProgress`, `ExerciseResult`

### Key Architecture Decisions Already Made

- PostgreSQL uses `app` schema (not `public`) to avoid conflicts with homelab
- All table models use `TABLE_ARGS` from `_table_args()` for schema routing
- String UUIDs for all PKs (not integers)
- Async SQLAlchemy throughout
- AI service uses OpenAI with mock fallback
- Database URL: `postgresql+asyncpg://learning_finnish:${FINNISH_DB_PASSWORD}@dobbybrain:5433/learning_finnish` (from backend/.env)

---

## What to Build

### Summary

Add spaced repetition to the existing `Word` and `UserWord` models, plus new tables for inflections, verb forms, concepts, and exercise logging. Create new API endpoints for the exercise flow that OpenClaw will call.

### Architecture of New Endpoints

```
OpenClaw daily cron
    │
    ├─ GET  /api/exercise/next        → returns words + concepts to practice
    ├─ POST /api/exercise/result      → submits scores, updates priorities
    │
    ├─ POST /api/words                → add word (triggers inflection generation)
    ├─ GET  /api/words/:id/inflections → get inflection table for a word
    │
    └─ GET  /api/stats                → dashboard data
        GET  /api/settings            → current level, config
        PUT  /api/settings            → update level, config
```

---

## Step 1: Extend Existing Models + Add New Tables

### 1.1 Add columns to existing `Word` model

Add these columns to the `Word` class in `models_db.py`. Do NOT remove existing columns — extend only.

```python
# Add to Word class (spaced repetition fields)
danish_translation = Column(String(255), nullable=True)  # Danish translation (preferred)
tags = Column(Text, nullable=True)  # JSON array of tags, e.g. '["food", "travel"]'

# Spaced repetition state
priority = Column(Float, default=1.0, index=True)  # 1.0 = needs practice, 0.0 = mastered
times_served = Column(Integer, default=0)
total_score = Column(Float, default=0.0)
last_score = Column(Float, nullable=True)
last_served = Column(DateTime(timezone=True), nullable=True)
```

**IMPORTANT:** The existing `grammatical_forms` column stores JSON as Text. The new `inflections` and `verb_forms` tables below provide a normalized version. Both can coexist — the JSON column is for quick display, the tables are for structured querying.

### 1.2 Add new tables

Add these new model classes to `models_db.py`:

```python
class Inflection(Base):
    """Finnish noun/adjective inflections by case"""
    __tablename__ = "inflections"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    word_id = Column(String, ForeignKey("words.id", ondelete="CASCADE"), index=True)
    case_name = Column(String(100), nullable=False)  # e.g. 'nominatiivi', 'partitiivi', 'genetiivi'
    singular = Column(String(255), nullable=True)
    plural = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    word = relationship("Word", back_populates="inflections")


class VerbForm(Base):
    """Finnish verb conjugations"""
    __tablename__ = "verb_forms"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    word_id = Column(String, ForeignKey("words.id", ondelete="CASCADE"), index=True)
    form_name = Column(String(100), nullable=False)  # e.g. 'minä/preesens', 'sinä/imperfekti'
    form_value = Column(String(255), nullable=False)
    tense = Column(String(100), nullable=True)  # 'preesens', 'imperfekti', 'konditionaali'
    notes = Column(Text, nullable=True)

    # Relationships
    word = relationship("Word", back_populates="verb_forms")


class Concept(Base):
    """Grammatical concepts (cases, verb types, etc.)"""
    __tablename__ = "concepts"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    examples = Column(Text, nullable=True)  # JSON
    tags = Column(Text, nullable=True)  # JSON array

    # Spaced repetition
    priority = Column(Float, default=1.0, index=True)
    times_served = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    last_score = Column(Float, nullable=True)
    last_served = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WordConcept(Base):
    """Link words to concepts they exercise"""
    __tablename__ = "word_concepts"
    __table_args__ = TABLE_ARGS

    word_id = Column(String, ForeignKey("words.id", ondelete="CASCADE"), primary_key=True)
    concept_id = Column(String, ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True)


class SpacedExerciseLog(Base):
    """Log of spaced repetition exercises (separate from lesson-based ExerciseResult)"""
    __tablename__ = "spaced_exercise_log"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    exercise_type = Column(String(100), nullable=False)  # 'translation', 'fill_blank', 'conjugation'
    level_used = Column(Integer, nullable=True)
    words_used = Column(Text, nullable=True)  # JSON array of word IDs
    concepts_used = Column(Text, nullable=True)  # JSON array of concept IDs
    prompt_sent = Column(Text, nullable=True)
    user_response = Column(Text, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    word_scores = Column(Text, nullable=True)  # JSON: [{"word_id": "...", "score": 7, "feedback": "..."}]
    concept_scores = Column(Text, nullable=True)  # JSON: [{"concept_id": "...", "score": 5, "feedback": "..."}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AppSetting(Base):
    """System settings (level, preferences)"""
    __tablename__ = "app_settings"
    __table_args__ = TABLE_ARGS

    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)  # JSON value
```

### 1.3 Add relationships to existing Word model

Add these `relationship()` lines to the `Word` class in `models_db.py`:

```python
# Add to Word class
inflections = relationship("Inflection", back_populates="word", cascade="all, delete-orphan")
verb_forms = relationship("VerbForm", back_populates="word", cascade="all, delete-orphan")
```

### 1.4 Add `import uuid` at the top of `models_db.py` if not already present.

### 1.5 Handle ForeignKey references with schema

**CRITICAL:** Because the app uses the `app` schema in PostgreSQL, ForeignKey strings must include the schema. The existing code uses bare table names like `ForeignKey("words.id")`. Check if these resolve correctly with the `search_path` set in `database.py`. If the new tables fail to create because FK references can't find the target table, you may need to prefix them:

```python
# If bare references fail:
ForeignKey(f"{APP_SCHEMA}.words.id", ondelete="CASCADE")
```

Test table creation before proceeding. Run the app and check logs for errors.

---

## Step 2: Database Migration

Since the project uses `init_db()` (which calls `Base.metadata.create_all`), new tables will be auto-created on startup. But adding columns to existing tables requires manual migration.

### 2.1 Create an Alembic-free migration script

Create `backend/scripts/migrate_spaced_repetition.py`:

```python
"""
Migration script: Add spaced repetition columns and tables.
Run once after deploying the updated models.

Usage:
    cd backend
    python scripts/migrate_spaced_repetition.py
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, APP_SCHEMA

SCHEMA = APP_SCHEMA  # "app"

async def migrate():
    async with engine.begin() as conn:
        # Add new columns to words table (IF NOT EXISTS prevents errors on re-run)
        columns_to_add = [
            ("danish_translation", "VARCHAR(255)"),
            ("tags", "TEXT"),
            ("priority", "FLOAT DEFAULT 1.0"),
            ("times_served", "INTEGER DEFAULT 0"),
            ("total_score", "FLOAT DEFAULT 0.0"),
            ("last_score", "FLOAT"),
            ("last_served", "TIMESTAMPTZ"),
        ]

        for col_name, col_type in columns_to_add:
            try:
                await conn.execute(text(
                    f'ALTER TABLE "{SCHEMA}"."words" ADD COLUMN IF NOT EXISTS "{col_name}" {col_type}'
                ))
                print(f"  ✓ Added column words.{col_name}")
            except Exception as e:
                print(f"  - Column words.{col_name} skipped: {e}")

        # Create index on priority
        try:
            await conn.execute(text(
                f'CREATE INDEX IF NOT EXISTS idx_words_priority ON "{SCHEMA}"."words" (priority DESC)'
            ))
            print("  ✓ Created index idx_words_priority")
        except Exception as e:
            print(f"  - Index skipped: {e}")

        # New tables are created by init_db() on app startup.
        # But let's also insert default settings.
        try:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"'))
        except Exception:
            pass

        # Insert default settings
        defaults = [
            ("level", "15"),
            ("exercise_word_count", "5"),
            ("random_ratio", "0.25"),
        ]
        for key, value in defaults:
            try:
                await conn.execute(text(
                    f"""INSERT INTO "{SCHEMA}"."app_settings" (key, value)
                        VALUES (:key, :value)
                        ON CONFLICT (key) DO NOTHING"""
                ), {"key": key, "value": value})
                print(f"  ✓ Setting {key} = {value}")
            except Exception as e:
                print(f"  - Setting {key} skipped (table may not exist yet): {e}")

        print("\nMigration complete. Start the app to create new tables via init_db().")

if __name__ == "__main__":
    asyncio.run(migrate())
```

### 2.2 Run the migration

```bash
cd backend
python scripts/migrate_spaced_repetition.py
```

Then restart the FastAPI app so `init_db()` creates the new tables (`inflections`, `verb_forms`, `concepts`, etc.).

---

## Step 3: Spaced Repetition Service

Create `backend/app/services/spaced_repetition.py`:

```python
"""
Spaced repetition engine for Finnish learning.

Key design:
- Event-driven priority only (no time decay) — pause-safe
- Decay scales with vocabulary size to prevent backlog
- 75% highest-priority words + 25% random for variety
"""

import json
import logging
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models_db import Word, Concept, AppSetting
from app.database import APP_SCHEMA

logger = logging.getLogger(__name__)


async def get_setting(db: AsyncSession, key: str, default=None):
    """Get a setting value from app_settings table."""
    stmt = select(AppSetting).where(AppSetting.key == key)
    result = await db.execute(stmt)
    setting = result.scalars().first()
    if setting:
        try:
            return json.loads(setting.value)
        except (json.JSONDecodeError, TypeError):
            return setting.value
    return default


async def set_setting(db: AsyncSession, key: str, value):
    """Set a setting value."""
    stmt = select(AppSetting).where(AppSetting.key == key)
    result = await db.execute(stmt)
    setting = result.scalars().first()
    json_value = json.dumps(value) if not isinstance(value, str) else value
    if setting:
        setting.value = json_value
    else:
        db.add(AppSetting(key=key, value=json_value))
    await db.commit()


async def select_exercise_words(db: AsyncSession) -> dict:
    """
    Select words for a daily exercise.

    Returns:
        {
            "words": [...],       # list of word dicts
            "concepts": [...],    # list of concept dicts
            "level": int,         # current difficulty level
            "exercise_word_count": int
        }
    """
    count = await get_setting(db, "exercise_word_count", 5)
    random_ratio = await get_setting(db, "random_ratio", 0.25)
    level = await get_setting(db, "level", 15)

    # Parse as numbers (settings stored as JSON strings)
    count = int(count) if count else 5
    random_ratio = float(random_ratio) if random_ratio else 0.25
    level = int(level) if level else 15

    n_random = max(1, round(count * random_ratio))
    n_priority = count - n_random

    # Highest priority words (not served today)
    priority_stmt = (
        select(Word)
        .where(Word.priority > 0)
        .order_by(Word.priority.desc())
        .limit(n_priority)
    )
    priority_result = await db.execute(priority_stmt)
    priority_words = priority_result.scalars().all()

    # Random words (excluding already selected)
    priority_ids = [w.id for w in priority_words]
    if priority_ids:
        random_stmt = (
            select(Word)
            .where(Word.id.notin_(priority_ids))
            .order_by(func.random())
            .limit(n_random)
        )
    else:
        random_stmt = (
            select(Word)
            .order_by(func.random())
            .limit(n_random)
        )
    random_result = await db.execute(random_stmt)
    random_words = random_result.scalars().all()

    all_words = priority_words + list(random_words)

    # Get concepts with highest priority (up to 2)
    concept_stmt = (
        select(Concept)
        .where(Concept.priority > 0)
        .order_by(Concept.priority.desc())
        .limit(2)
    )
    concept_result = await db.execute(concept_stmt)
    concepts = concept_result.scalars().all()

    def word_to_dict(w: Word) -> dict:
        return {
            "id": w.id,
            "finnish": w.finnish_word,
            "danish": w.danish_translation,
            "english": w.english_translation,
            "word_type": w.part_of_speech,
            "priority": w.priority,
            "tags": json.loads(w.tags) if w.tags else [],
        }

    def concept_to_dict(c: Concept) -> dict:
        return {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "priority": c.priority,
        }

    return {
        "words": [word_to_dict(w) for w in all_words],
        "concepts": [concept_to_dict(c) for c in concepts],
        "level": level,
        "exercise_word_count": count,
    }


async def update_priorities_after_exercise(
    db: AsyncSession,
    word_scores: list[dict],
    concept_scores: list[dict] | None = None,
):
    """
    Update word and concept priorities after an exercise.

    Event-driven: priorities only change when exercises happen.
    Decay scales with vocabulary size to prevent backlog.

    word_scores: [{"word_id": "uuid", "score": 7.5, "feedback": "..."}]
    concept_scores: [{"concept_id": "uuid", "score": 5, "feedback": "..."}]
    """
    # Get total word count for scaling
    count_result = await db.execute(select(func.count(Word.id)))
    total_words = count_result.scalar() or 1

    # Decay factor scales with vocabulary size
    decay_per_point = 1.0 / max(total_words, 1)

    for ws in word_scores:
        word_id = ws.get("word_id")
        score = float(ws.get("score", 5))

        # score 10 → priority decreases by 5 * decay_per_point
        # score 5  → no change
        # score 0  → priority increases by 5 * decay_per_point
        priority_change = (score - 5) * decay_per_point

        stmt = select(Word).where(Word.id == word_id)
        result = await db.execute(stmt)
        word = result.scalars().first()

        if word:
            new_priority = max(0.0, min(1.0, (word.priority or 1.0) - priority_change))
            word.priority = new_priority
            word.times_served = (word.times_served or 0) + 1
            word.total_score = (word.total_score or 0) + score
            word.last_score = score
            word.last_served = func.now()
            logger.info(f"Word {word.finnish_word}: score={score}, priority {word.priority:.3f} → {new_priority:.3f}")

    # Update concept priorities similarly
    if concept_scores:
        count_result = await db.execute(select(func.count(Concept.id)))
        total_concepts = count_result.scalar() or 1
        concept_decay = 1.0 / max(total_concepts, 1)

        for cs in concept_scores:
            concept_id = cs.get("concept_id")
            score = float(cs.get("score", 5))
            priority_change = (score - 5) * concept_decay

            stmt = select(Concept).where(Concept.id == concept_id)
            result = await db.execute(stmt)
            concept = result.scalars().first()

            if concept:
                new_priority = max(0.0, min(1.0, (concept.priority or 1.0) - priority_change))
                concept.priority = new_priority
                concept.times_served = (concept.times_served or 0) + 1
                concept.total_score = (concept.total_score or 0) + score
                concept.last_score = score
                concept.last_served = func.now()

    await db.commit()
```

---

## Step 4: Inflection Generation Service

Create `backend/app/services/inflection_service.py`:

This extends the existing `ai_service.py` pattern. It calls the LLM to generate Finnish inflections when a word is added, then stores them in the `inflections` and `verb_forms` tables.

```python
"""
LLM-powered Finnish inflection generator.
Called when a new word is added via API or OpenClaw.
"""

import json
import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models_db import Word, Inflection, VerbForm
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

NOUN_CASES = [
    "nominatiivi", "genetiivi", "partitiivi", "inessiivi", "elatiivi",
    "illatiivi", "adessiivi", "ablatiivi", "allatiivi", "essiivi",
    "translatiivi", "abessiivi"
]

VERB_PERSONS = ["minä", "sinä", "hän", "me", "te", "he"]
VERB_TENSES = ["preesens", "imperfekti"]


async def generate_and_store_inflections(db: AsyncSession, word: Word) -> dict:
    """
    Generate inflections for a word using the LLM, then store them in the DB.

    Returns dict with counts: {"inflections": N, "verb_forms": N}
    """
    pos = (word.part_of_speech or "noun").lower()

    if not ai_service.use_openai:
        logger.info(f"OpenAI not configured, skipping inflection generation for '{word.finnish_word}'")
        return {"inflections": 0, "verb_forms": 0}

    try:
        if pos == "verb":
            return await _generate_verb_forms(db, word)
        else:
            return await _generate_noun_adj_inflections(db, word)
    except Exception as e:
        logger.error(f"Failed to generate inflections for '{word.finnish_word}': {e}")
        return {"inflections": 0, "verb_forms": 0}


async def _generate_noun_adj_inflections(db: AsyncSession, word: Word) -> dict:
    """Generate noun/adjective case inflections."""
    prompt = f"""Generate all Finnish grammatical case forms for the word: "{word.finnish_word}" ({word.part_of_speech})
Translation: {word.danish_translation or word.english_translation}

Provide singular and plural for these cases:
{', '.join(NOUN_CASES)}

Return ONLY this JSON (no other text):
{{
  "inflections": [
    {{"case_name": "nominatiivi", "singular": "...", "plural": "..."}},
    ...
  ],
  "notes": "any irregularity notes"
}}"""

    try:
        response = await ai_service.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Finnish grammar expert. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=800,
        )

        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        data = json.loads(content)
        inflections = data.get("inflections", [])

        count = 0
        for infl in inflections:
            db.add(Inflection(
                id=str(uuid.uuid4()),
                word_id=word.id,
                case_name=infl.get("case_name", ""),
                singular=infl.get("singular"),
                plural=infl.get("plural"),
                notes=data.get("notes"),
            ))
            count += 1

        await db.commit()
        logger.info(f"Generated {count} inflections for '{word.finnish_word}'")
        return {"inflections": count, "verb_forms": 0}

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse inflection response for '{word.finnish_word}': {e}")
        return {"inflections": 0, "verb_forms": 0}


async def _generate_verb_forms(db: AsyncSession, word: Word) -> dict:
    """Generate verb conjugation forms."""
    prompt = f"""Generate Finnish verb conjugation forms for: "{word.finnish_word}"
Translation: {word.danish_translation or word.english_translation}

Provide these forms:
- All persons (minä, sinä, hän, me, te, he) in preesens and imperfekti
- passiivi (preesens and imperfekti)
- konditionaali (minä)
- imperatiivi (sinä)

Return ONLY this JSON (no other text):
{{
  "verb_forms": [
    {{"form_name": "minä", "form_value": "...", "tense": "preesens"}},
    {{"form_name": "minä", "form_value": "...", "tense": "imperfekti"}},
    ...
  ],
  "notes": "verb type and any irregularity notes"
}}"""

    try:
        response = await ai_service.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Finnish grammar expert. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=800,
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        data = json.loads(content)
        forms = data.get("verb_forms", [])

        count = 0
        for form in forms:
            db.add(VerbForm(
                id=str(uuid.uuid4()),
                word_id=word.id,
                form_name=form.get("form_name", ""),
                form_value=form.get("form_value", ""),
                tense=form.get("tense"),
                notes=data.get("notes"),
            ))
            count += 1

        await db.commit()
        logger.info(f"Generated {count} verb forms for '{word.finnish_word}'")
        return {"inflections": 0, "verb_forms": count}

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse verb form response for '{word.finnish_word}': {e}")
        return {"inflections": 0, "verb_forms": 0}
```

---

## Step 5: New API Router — Exercise Endpoints

Create `backend/app/routers/exercise.py`:

This is what OpenClaw calls. It has 3 endpoints:
1. `GET /exercise/next` — get words to practice
2. `POST /exercise/result` — submit scores
3. `GET /exercise/history` — past exercises

```python
"""Exercise endpoints for spaced repetition (called by OpenClaw)."""

import json
import logging
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models_db import SpacedExerciseLog
from app.services.spaced_repetition import (
    select_exercise_words,
    update_priorities_after_exercise,
    get_setting,
    set_setting,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exercise", tags=["exercise"])


@router.get("/next")
async def get_next_exercise(db: AsyncSession = Depends(get_db)):
    """
    Get the next batch of words and concepts for an exercise.
    Called by OpenClaw daily cron.

    Returns words (75% priority + 25% random), concepts, and current level.
    """
    data = await select_exercise_words(db)
    return data


@router.post("/result")
async def submit_exercise_result(
    request: dict,  # Accept raw dict for flexibility from OpenClaw
    db: AsyncSession = Depends(get_db),
):
    """
    Submit exercise scores and update word priorities.
    Called by OpenClaw after scoring the user's response.

    Expected body:
    {
        "exercise_type": "translation",
        "prompt_sent": "Finnish sentences that were sent",
        "user_response": "What the user replied",
        "ai_feedback": "Overall feedback from the scoring LLM",
        "word_scores": [{"word_id": "uuid", "score": 7.5, "feedback": "..."}],
        "concept_scores": [{"concept_id": "uuid", "score": 5, "feedback": "..."}]
    }
    """
    word_scores = request.get("word_scores", [])
    concept_scores = request.get("concept_scores", [])
    level = await get_setting(db, "level", 15)

    # Update priorities
    await update_priorities_after_exercise(db, word_scores, concept_scores)

    # Log the exercise
    log_entry = SpacedExerciseLog(
        id=str(uuid.uuid4()),
        exercise_type=request.get("exercise_type", "translation"),
        level_used=int(level) if level else 15,
        words_used=json.dumps([ws.get("word_id") for ws in word_scores]),
        concepts_used=json.dumps([cs.get("concept_id") for cs in concept_scores]) if concept_scores else None,
        prompt_sent=request.get("prompt_sent"),
        user_response=request.get("user_response"),
        ai_feedback=request.get("ai_feedback"),
        word_scores=json.dumps(word_scores),
        concept_scores=json.dumps(concept_scores) if concept_scores else None,
    )
    db.add(log_entry)
    await db.commit()

    return {
        "status": "ok",
        "words_scored": len(word_scores),
        "concepts_scored": len(concept_scores) if concept_scores else 0,
    }


@router.get("/history")
async def get_exercise_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get past exercise history with scores and feedback."""
    from sqlalchemy import select

    stmt = (
        select(SpacedExerciseLog)
        .order_by(SpacedExerciseLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "exercise_type": log.exercise_type,
            "level_used": log.level_used,
            "prompt_sent": log.prompt_sent,
            "user_response": log.user_response,
            "ai_feedback": log.ai_feedback,
            "word_scores": json.loads(log.word_scores) if log.word_scores else [],
            "concept_scores": json.loads(log.concept_scores) if log.concept_scores else [],
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
```

---

## Step 6: Settings & Stats Router

Create `backend/app/routers/settings.py`:

```python
"""Settings and stats endpoints."""

import json
import logging
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models_db import Word, Concept, SpacedExerciseLog, AppSetting
from app.services.spaced_repetition import get_setting, set_setting

logger = logging.getLogger(__name__)
router = APIRouter(tags=["settings"])


@router.get("/settings")
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    """Get all app settings."""
    stmt = select(AppSetting)
    result = await db.execute(stmt)
    settings = result.scalars().all()
    return {s.key: json.loads(s.value) if s.value else None for s in settings}


@router.put("/settings")
async def update_settings(request: dict, db: AsyncSession = Depends(get_db)):
    """
    Update one or more settings.
    Body: {"level": 20, "exercise_word_count": 6}
    """
    for key, value in request.items():
        await set_setting(db, key, value)
    return {"status": "ok", "updated": list(request.keys())}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Dashboard statistics."""
    # Total words
    total_words = (await db.execute(select(func.count(Word.id)))).scalar() or 0

    # Words by priority bucket
    mastered = (await db.execute(
        select(func.count(Word.id)).where(Word.priority < 0.2)
    )).scalar() or 0

    learning = (await db.execute(
        select(func.count(Word.id)).where(Word.priority.between(0.2, 0.7))
    )).scalar() or 0

    needs_work = (await db.execute(
        select(func.count(Word.id)).where(Word.priority > 0.7)
    )).scalar() or 0

    # Average score
    avg_score_result = (await db.execute(
        select(func.avg(Word.last_score)).where(Word.last_score.isnot(None))
    )).scalar()

    # Total exercises
    total_exercises = (await db.execute(
        select(func.count(SpacedExerciseLog.id))
    )).scalar() or 0

    # Total concepts
    total_concepts = (await db.execute(select(func.count(Concept.id)))).scalar() or 0

    # Current level
    level = await get_setting(db, "level", 15)

    return {
        "total_words": total_words,
        "mastered": mastered,
        "learning": learning,
        "needs_work": needs_work,
        "mastery_percent": round(mastered / total_words * 100, 1) if total_words > 0 else 0,
        "avg_score": round(float(avg_score_result), 1) if avg_score_result else None,
        "total_exercises": total_exercises,
        "total_concepts": total_concepts,
        "level": int(level) if level else 15,
    }
```

---

## Step 7: Register New Routers

In `backend/app/main.py`, add the new router imports and registrations:

```python
# Add imports
from app.routers import health, lessons, vocabulary, progress, words, exercise, settings as settings_router

# Add router registrations (after existing ones)
app.include_router(exercise.router, prefix=settings.api_prefix)
app.include_router(settings_router.router, prefix=settings.api_prefix)
```

---

## Step 8: Extend Word Creation to Trigger Inflection Generation

In `backend/app/routers/words.py`, modify the `save_word` endpoint. After a new `Word` is created and flushed, add:

```python
# Add import at top
from app.services.inflection_service import generate_and_store_inflections

# Inside save_word(), after the line: db.add(word_db); await db.flush()
# Add:
inflection_result = await generate_and_store_inflections(db, word_db)
logger.info(f"Generated inflections for '{word_db.finnish_word}': {inflection_result}")
```

Also add a **new endpoint** for getting inflections:

```python
@router.get("/{word_id}/inflections")
async def get_word_inflections(
    word_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all inflections/verb forms for a word."""
    from sqlalchemy.orm import selectinload

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
            {"case_name": i.case_name, "singular": i.singular, "plural": i.plural, "notes": i.notes}
            for i in (word.inflections or [])
        ],
        "verb_forms": [
            {"form_name": v.form_name, "form_value": v.form_value, "tense": v.tense, "notes": v.notes}
            for v in (word.verb_forms or [])
        ],
    }
```

And an endpoint to **regenerate inflections**:

```python
@router.post("/{word_id}/inflections/generate")
async def regenerate_inflections(
    word_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Re-generate inflections for a word using the LLM."""
    from app.services.inflection_service import generate_and_store_inflections
    from app.models_db import Inflection, VerbForm

    stmt = select(Word).where(Word.id == word_id)
    result = await db.execute(stmt)
    word = result.scalars().first()

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    # Delete existing inflections
    await db.execute(
        select(Inflection).where(Inflection.word_id == word_id).execution_options(synchronize_session=False)
    )
    # Use delete instead
    from sqlalchemy import delete
    await db.execute(delete(Inflection).where(Inflection.word_id == word_id))
    await db.execute(delete(VerbForm).where(VerbForm.word_id == word_id))
    await db.commit()

    # Regenerate
    inflection_result = await generate_and_store_inflections(db, word)
    return {"status": "ok", **inflection_result}
```

---

## Step 9: Add a Simple Word Creation Endpoint for OpenClaw

The existing `save_word` endpoint requires a `user_id`. Add a simpler endpoint for OpenClaw to add words directly:

Add to `backend/app/routers/words.py`:

```python
@router.post("/add")
async def add_word_simple(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Simple word addition endpoint (for OpenClaw).

    Body:
    {
        "finnish": "talo",
        "danish": "hus",
        "english": "house",
        "word_type": "noun",
        "tags": ["basics"]
    }
    """
    from app.services.inflection_service import generate_and_store_inflections

    finnish = request.get("finnish", "").strip()
    if not finnish:
        raise HTTPException(status_code=400, detail="finnish is required")

    # Check if word already exists
    stmt = select(Word).where(Word.finnish_word.ilike(finnish))
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        return {"status": "exists", "word_id": existing.id, "finnish": existing.finnish_word}

    word = Word(
        id=str(uuid.uuid4()),
        finnish_word=finnish,
        danish_translation=request.get("danish"),
        english_translation=request.get("english", finnish),
        part_of_speech=request.get("word_type", "noun"),
        tags=json.dumps(request.get("tags", [])),
        priority=1.0,
    )
    db.add(word)
    await db.flush()

    # Generate inflections
    infl_result = await generate_and_store_inflections(db, word)
    await db.commit()

    return {
        "status": "created",
        "word_id": word.id,
        "finnish": word.finnish_word,
        "inflections_generated": infl_result,
    }
```

---

## Step 10: Test Everything

### 10.1 Start the app

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check logs for table creation errors.

### 10.2 Run migration (if columns are missing)

```bash
python scripts/migrate_spaced_repetition.py
```

### 10.3 Test endpoints with curl

```bash
BASE=http://localhost:8000/api

# Health check
curl $BASE/health/simple

# Add a word
curl -X POST $BASE/words/add \
  -H "Content-Type: application/json" \
  -d '{"finnish": "talo", "danish": "hus", "english": "house", "word_type": "noun", "tags": ["basics"]}'

# Get inflections
curl $BASE/words/WORD_ID_HERE/inflections

# Get exercise batch
curl $BASE/exercise/next

# Get settings
curl $BASE/settings

# Update level
curl -X PUT $BASE/settings \
  -H "Content-Type: application/json" \
  -d '{"level": 20}'

# Submit exercise result
curl -X POST $BASE/exercise/result \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_type": "translation",
    "prompt_sent": "Talo on suuri.",
    "user_response": "The house is big.",
    "word_scores": [{"word_id": "WORD_ID", "score": 8, "feedback": "Godt!"}]
  }'

# Check stats
curl $BASE/stats

# Exercise history
curl $BASE/exercise/history
```

### 10.4 Verify priority updates

After submitting an exercise result:
1. Check that the word's `priority` changed
2. Check that `times_served` incremented
3. Check that `/exercise/next` returns words with highest priority first

---

## Verification Checklist

| Check | Command/Action |
|-------|----------------|
| App starts without errors | `uvicorn app.main:app` — no table creation failures |
| New tables exist | Check `/docs` swagger — new endpoints visible |
| Word creation works | `POST /words/add` returns `created` |
| Inflections generated | `GET /words/:id/inflections` returns case forms |
| Exercise selection works | `GET /exercise/next` returns words + level |
| Priority updates work | `POST /exercise/result` then check word priority changed |
| Settings work | `GET /settings` returns level=15 |
| Stats work | `GET /stats` returns word counts and mastery % |
| History works | `GET /exercise/history` returns past exercises |

---

## Files Created/Modified Summary

| Action | File |
|--------|------|
| **Modified** | `backend/app/models_db.py` — new columns on Word, new tables |
| **Modified** | `backend/app/models/__init__.py` — new Pydantic schemas (if needed) |
| **Modified** | `backend/app/main.py` — register new routers |
| **Modified** | `backend/app/routers/words.py` — inflection endpoints, `/add` endpoint |
| **Created** | `backend/app/routers/exercise.py` — exercise flow endpoints |
| **Created** | `backend/app/routers/settings.py` — settings + stats |
| **Created** | `backend/app/services/spaced_repetition.py` — priority engine |
| **Created** | `backend/app/services/inflection_service.py` — LLM inflection generator |
| **Created** | `backend/scripts/migrate_spaced_repetition.py` — migration script |