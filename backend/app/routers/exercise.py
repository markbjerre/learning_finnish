"""Exercise endpoints for spaced repetition (called by OpenClaw)."""

import json
import logging
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models_db import SpacedExerciseLog
from app.services.spaced_repetition import (
    select_exercise_words,
    update_priorities_after_exercise,
    get_setting,
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
    request: dict,
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

    await update_priorities_after_exercise(db, word_scores, concept_scores)

    log_entry = SpacedExerciseLog(
        id=str(uuid.uuid4()),
        exercise_type=request.get("exercise_type", "translation"),
        level_used=int(level) if level else 15,
        words_used=json.dumps([ws.get("word_id") for ws in word_scores]),
        concepts_used=(
            json.dumps([cs.get("concept_id") for cs in concept_scores])
            if concept_scores
            else None
        ),
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
