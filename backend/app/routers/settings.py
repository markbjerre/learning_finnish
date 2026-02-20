"""Settings and stats endpoints."""

import json
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models_db import Word, Concept, SpacedExerciseLog, AppSetting
from app.services.spaced_repetition import get_setting, set_setting

logger = logging.getLogger(__name__)
router = APIRouter(tags=["settings"])


@router.get("/stats/chart")
async def get_stats_chart(
    days: int = Query(14, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Exercise count per day for the last N days (for progress chart)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = select(SpacedExerciseLog.created_at).where(SpacedExerciseLog.created_at >= cutoff)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    by_date = {}
    for row in rows:
        dt = row[0] if isinstance(row, (list, tuple)) else row
        if dt is not None:
            d = dt.date() if hasattr(dt, "date") else datetime.fromisoformat(str(dt).replace("Z", "+00:00")).date()
            by_date[str(d)] = by_date.get(str(d), 0) + 1
    return [{"date": k, "count": v} for k, v in sorted(by_date.items())]


@router.get("/settings")
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    """Get all app settings."""
    stmt = select(AppSetting)
    result = await db.execute(stmt)
    settings = result.scalars().all()
    out = {}
    for s in settings:
        try:
            out[s.key] = json.loads(s.value) if s.value else None
        except (json.JSONDecodeError, TypeError):
            out[s.key] = s.value
    return out


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
    total_words = (await db.execute(select(func.count(Word.id)))).scalar() or 0

    mastered = (
        await db.execute(select(func.count(Word.id)).where(Word.priority < 0.2))
    ).scalar() or 0

    learning = (
        await db.execute(
            select(func.count(Word.id)).where(Word.priority.between(0.2, 0.7))
        )
    ).scalar() or 0

    needs_work = (
        await db.execute(select(func.count(Word.id)).where(Word.priority > 0.7))
    ).scalar() or 0

    avg_score_row = (
        await db.execute(
            select(func.avg(Word.last_score)).where(Word.last_score.isnot(None))
        )
    ).scalar()
    avg_score_result = float(avg_score_row) if avg_score_row is not None else None

    total_exercises = (
        await db.execute(select(func.count(SpacedExerciseLog.id)))
    ).scalar() or 0

    total_concepts = (
        await db.execute(select(func.count(Concept.id)))
    ).scalar() or 0

    level = await get_setting(db, "level", 15)

    # Streak: consecutive days with at least one exercise
    streak = 0
    stmt = select(SpacedExerciseLog.created_at).order_by(SpacedExerciseLog.created_at.desc())
    logs = (await db.execute(stmt)).scalars().all()
    if logs:
        seen_dates = set()
        for row in logs:
            dt = row[0]
            if dt:
                d = dt.date() if hasattr(dt, "date") else datetime.fromisoformat(str(dt).replace("Z", "+00:00")).date()
                seen_dates.add(d)
        today = datetime.now(timezone.utc).date()
        d = today
        while d in seen_dates:
            streak += 1
            d = d - timedelta(days=1)

    return {
        "total_words": total_words,
        "mastered": mastered,
        "learning": learning,
        "needs_work": needs_work,
        "mastery_percent": round(mastered / total_words * 100, 1) if total_words > 0 else 0,
        "avg_score": round(avg_score_result, 1) if avg_score_result is not None else None,
        "total_exercises": total_exercises,
        "total_concepts": total_concepts,
        "level": int(level) if level else 15,
        "streak_days": streak,
    }
