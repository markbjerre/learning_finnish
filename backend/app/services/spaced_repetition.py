"""
Spaced repetition engine for Finnish learning.

Key design:
- Event-driven priority only (no time decay) — pause-safe
- Decay scales with vocabulary size to prevent backlog
- 75% highest-priority words + 25% random for variety
"""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_db import Word, Concept, AppSetting

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

    count = int(count) if count else 5
    random_ratio = float(random_ratio) if random_ratio else 0.25
    level = int(level) if level else 15

    n_random = max(1, round(count * random_ratio))
    n_priority = count - n_random

    # Highest priority words
    priority_stmt = (
        select(Word)
        .where(Word.priority > 0)
        .order_by(Word.priority.desc())
        .limit(n_priority)
    )
    priority_result = await db.execute(priority_stmt)
    priority_words = list(priority_result.scalars().all())

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
    random_words = list(random_result.scalars().all())

    all_words = priority_words + random_words

    # Get concepts with highest priority (up to 2)
    concept_stmt = (
        select(Concept)
        .where(Concept.priority > 0)
        .order_by(Concept.priority.desc())
        .limit(2)
    )
    concept_result = await db.execute(concept_stmt)
    concepts = list(concept_result.scalars().all())

    def word_to_dict(w: Word) -> dict:
        return {
            "id": w.id,
            "finnish": w.finnish_word,
            "danish": getattr(w, "danish_translation", None),
            "english": w.english_translation,
            "word_type": w.part_of_speech,
            "priority": getattr(w, "priority", 1.0),
            "tags": json.loads(w.tags) if getattr(w, "tags", None) else [],
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
    count_result = await db.execute(select(func.count(Word.id)))
    total_words = count_result.scalar() or 1

    decay_per_point = 1.0 / max(total_words, 1)
    now = datetime.now(timezone.utc)

    for ws in word_scores:
        word_id = ws.get("word_id")
        score = float(ws.get("score", 5))

        priority_change = (score - 5) * decay_per_point

        stmt = select(Word).where(Word.id == word_id)
        result = await db.execute(stmt)
        word = result.scalars().first()

        if word:
            current_priority = getattr(word, "priority", 1.0) or 1.0
            new_priority = max(0.0, min(1.0, current_priority - priority_change))
            word.priority = new_priority
            word.times_served = (getattr(word, "times_served", 0) or 0) + 1
            word.total_score = (getattr(word, "total_score", 0) or 0) + score
            word.last_score = score
            word.last_served = now
            logger.info(
                f"Word {word.finnish_word}: score={score}, "
                f"priority {current_priority:.3f} -> {new_priority:.3f}"
            )

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
                current_priority = concept.priority or 1.0
                new_priority = max(0.0, min(1.0, current_priority - priority_change))
                concept.priority = new_priority
                concept.times_served = (concept.times_served or 0) + 1
                concept.total_score = (concept.total_score or 0) + score
                concept.last_score = score
                concept.last_served = now

    await db.commit()
