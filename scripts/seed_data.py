#!/usr/bin/env python3
"""
Seed Learning Finnish database with example data (min 5 rows per table).

Usage:
  python scripts/seed_data.py
  python scripts/seed_data.py --use-sqlite   # Use SQLite for local testing
  DATABASE_URL=postgresql+asyncpg://... python scripts/seed_data.py
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

# Add app to path (works from repo or container)
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
backend_path = project_root / "backend"
app_path = backend_path
sys.path.insert(0, str(app_path))
os.chdir(app_path)

# Parse --use-sqlite before loading app (must set env before config loads)
if "--use-sqlite" in sys.argv:
    os.environ["DATABASE_URL"] = ""
    sys.argv = [a for a in sys.argv if a != "--use-sqlite"]

# Load env before importing app
from dotenv import load_dotenv
if backend_path.exists():
    load_dotenv(backend_path / ".env")
load_dotenv(project_root / ".env")


async def seed():
    from app.config import settings
    from app.database import init_db, async_session
    from app.models_db import (
        Lesson, VocabularyList, VocabularyWord, Exercise,
        User, LessonProgress, ExerciseResult,
        Word, UserWord,
        DifficultyEnum, ExerciseTypeEnum, WordStatusEnum,
    )

    if not settings.database_url or "sqlite" in settings.database_url:
        print("Using SQLite (no DATABASE_URL or sqlite)")
    else:
        print("Using PostgreSQL:", settings.database_url.split("@")[-1][:50] + "...")

    # Ensure tables exist (required for SQLite; safe for PostgreSQL)
    await init_db()

    async with async_session() as session:
        # 1. Lessons (5)
        lessons = [
            Lesson(id="lesson-1", title="Greetings", description="Basic greetings in Finnish", difficulty=DifficultyEnum.BEGINNER, order=1, estimated_duration_minutes=15),
            Lesson(id="lesson-2", title="Numbers 1-10", description="Learn numbers", difficulty=DifficultyEnum.BEGINNER, order=2, estimated_duration_minutes=20),
            Lesson(id="lesson-3", title="Colors", description="Common colors", difficulty=DifficultyEnum.ELEMENTARY, order=3, estimated_duration_minutes=15),
            Lesson(id="lesson-4", title="Family", description="Family members", difficulty=DifficultyEnum.ELEMENTARY, order=4, estimated_duration_minutes=25),
            Lesson(id="lesson-5", title="Food & Drink", description="Common food vocabulary", difficulty=DifficultyEnum.INTERMEDIATE, order=5, estimated_duration_minutes=30),
        ]
        for l in lessons:
            session.add(l)
        await session.flush()
        print("  [OK] lessons: 5 rows")

        # 2. Users (5)
        users = [
            User(id="user-1", email="anna@example.com", username="anna"),
            User(id="user-2", email="mikko@example.com", username="mikko"),
            User(id="user-3", email="liisa@example.com", username="liisa"),
            User(id="user-4", email="jussi@example.com", username="jussi"),
            User(id="user-5", email="sanna@example.com", username="sanna"),
        ]
        for u in users:
            session.add(u)
        await session.flush()
        print("  [OK] users: 5 rows")

        # 3. Words (5) - dictionary
        words = [
            Word(id="word-1", finnish_word="kissa", english_translation="cat", part_of_speech="noun", grammatical_forms='{"nominative":"kissa"}'),
            Word(id="word-2", finnish_word="koira", english_translation="dog", part_of_speech="noun", grammatical_forms='{"nominative":"koira"}'),
            Word(id="word-3", finnish_word="talo", english_translation="house", part_of_speech="noun", grammatical_forms='{"nominative":"talo"}'),
            Word(id="word-4", finnish_word="omena", english_translation="apple", part_of_speech="noun", grammatical_forms='{"nominative":"omena"}'),
            Word(id="word-5", finnish_word="vesi", english_translation="water", part_of_speech="noun", grammatical_forms='{"nominative":"vesi"}'),
        ]
        for w in words:
            session.add(w)
        await session.flush()
        print("  [OK] words: 5 rows")

        # 4. VocabularyLists (5) - need lesson_id
        vocab_lists = [
            VocabularyList(id="vl-1", title="Greetings vocab", description="Basic words", difficulty=DifficultyEnum.BEGINNER, lesson_id="lesson-1"),
            VocabularyList(id="vl-2", title="Numbers vocab", description="1-10", difficulty=DifficultyEnum.BEGINNER, lesson_id="lesson-2"),
            VocabularyList(id="vl-3", title="Colors vocab", description="Colors", difficulty=DifficultyEnum.ELEMENTARY, lesson_id="lesson-3"),
            VocabularyList(id="vl-4", title="Family vocab", description="Family", difficulty=DifficultyEnum.ELEMENTARY, lesson_id="lesson-4"),
            VocabularyList(id="vl-5", title="Food vocab", description="Food", difficulty=DifficultyEnum.INTERMEDIATE, lesson_id="lesson-5"),
        ]
        for v in vocab_lists:
            session.add(v)
        await session.flush()
        print("  [OK] vocabulary_lists: 5 rows")

        # 5. VocabularyWords (5) - need vocabulary_list_id
        vocab_words = [
            VocabularyWord(id="vw-1", finnish="hei", english="hello", part_of_speech="interjection", vocabulary_list_id="vl-1"),
            VocabularyWord(id="vw-2", finnish="yksi", english="one", part_of_speech="numeral", vocabulary_list_id="vl-2"),
            VocabularyWord(id="vw-3", finnish="punainen", english="red", part_of_speech="adjective", vocabulary_list_id="vl-3"),
            VocabularyWord(id="vw-4", finnish="isä", english="father", part_of_speech="noun", vocabulary_list_id="vl-4"),
            VocabularyWord(id="vw-5", finnish="leipä", english="bread", part_of_speech="noun", vocabulary_list_id="vl-5"),
        ]
        for vw in vocab_words:
            session.add(vw)
        await session.flush()
        print("  [OK] vocabulary_words: 5 rows")

        # 6. Exercises (5) - need lesson_id
        exercises = [
            Exercise(id="ex-1", lesson_id="lesson-1", type=ExerciseTypeEnum.MULTIPLE_CHOICE, question="How do you say hello?", options='["hei","moi","terve"]', correct_answer="hei", difficulty=DifficultyEnum.BEGINNER),
            Exercise(id="ex-2", lesson_id="lesson-2", type=ExerciseTypeEnum.FILL_IN_BLANK, question="Three in Finnish is ___", options='[]', correct_answer="kolme", difficulty=DifficultyEnum.BEGINNER),
            Exercise(id="ex-3", lesson_id="lesson-3", type=ExerciseTypeEnum.TRANSLATION, question="Translate: sininen", options='[]', correct_answer="blue", difficulty=DifficultyEnum.ELEMENTARY),
            Exercise(id="ex-4", lesson_id="lesson-4", type=ExerciseTypeEnum.MULTIPLE_CHOICE, question="Mother in Finnish?", options='["äiti","isä","sisko"]', correct_answer="äiti", difficulty=DifficultyEnum.ELEMENTARY),
            Exercise(id="ex-5", lesson_id="lesson-5", type=ExerciseTypeEnum.TRANSLATION, question="Translate: maito", options='[]', correct_answer="milk", difficulty=DifficultyEnum.INTERMEDIATE),
        ]
        for e in exercises:
            session.add(e)
        await session.flush()
        print("  [OK] exercises: 5 rows")

        # 7. UserWords (5) - need user_id, word_id
        user_words = [
            UserWord(id="uw-1", user_id="user-1", word_id="word-1", status=WordStatusEnum.LEARNING, proficiency=50),
            UserWord(id="uw-2", user_id="user-1", word_id="word-2", status=WordStatusEnum.RECENT, proficiency=0),
            UserWord(id="uw-3", user_id="user-2", word_id="word-3", status=WordStatusEnum.MASTERED, proficiency=100),
            UserWord(id="uw-4", user_id="user-2", word_id="word-4", status=WordStatusEnum.LEARNING, proficiency=30),
            UserWord(id="uw-5", user_id="user-3", word_id="word-5", status=WordStatusEnum.RECENT, proficiency=0),
        ]
        for uw in user_words:
            session.add(uw)
        await session.flush()
        print("  [OK] user_words: 5 rows")

        # 8. LessonProgress (5) - need user_id, lesson_id
        lesson_progress = [
            LessonProgress(id="lp-1", user_id="user-1", lesson_id="lesson-1", status="completed", exercises_completed=5, exercises_correct=4),
            LessonProgress(id="lp-2", user_id="user-1", lesson_id="lesson-2", status="in_progress", exercises_completed=2, exercises_correct=2),
            LessonProgress(id="lp-3", user_id="user-2", lesson_id="lesson-1", status="completed", exercises_completed=5, exercises_correct=5),
            LessonProgress(id="lp-4", user_id="user-2", lesson_id="lesson-3", status="in_progress", exercises_completed=1, exercises_correct=1),
            LessonProgress(id="lp-5", user_id="user-3", lesson_id="lesson-1", status="in_progress", exercises_completed=0, exercises_correct=0),
        ]
        for lp in lesson_progress:
            session.add(lp)
        await session.flush()
        print("  [OK] lesson_progress: 5 rows")

        # 9. ExerciseResults (5) - need user_id, exercise_id, lesson_progress_id
        exercise_results = [
            ExerciseResult(id="er-1", user_id="user-1", exercise_id="ex-1", lesson_progress_id="lp-1", correct=True, user_answer="hei", time_spent_seconds=5),
            ExerciseResult(id="er-2", user_id="user-1", exercise_id="ex-2", lesson_progress_id="lp-2", correct=True, user_answer="kolme", time_spent_seconds=8),
            ExerciseResult(id="er-3", user_id="user-2", exercise_id="ex-1", lesson_progress_id="lp-3", correct=True, user_answer="hei", time_spent_seconds=3),
            ExerciseResult(id="er-4", user_id="user-2", exercise_id="ex-3", lesson_progress_id="lp-4", correct=False, user_answer="green", time_spent_seconds=10),
            ExerciseResult(id="er-5", user_id="user-3", exercise_id="ex-1", lesson_progress_id="lp-5", correct=False, user_answer="moi", time_spent_seconds=12),
        ]
        for er in exercise_results:
            session.add(er)

        await session.commit()
        print("  [OK] exercise_results: 5 rows")

    print("\nSeed complete. All tables have at least 5 rows.")


if __name__ == "__main__":
    asyncio.run(seed())
