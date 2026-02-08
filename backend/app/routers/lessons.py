"""Lesson endpoints for Learning Finnish API"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models import (
    Lesson,
    LessonPreview,
    DifficultyLevel,
    Exercise,
    ExerciseType,
    VocabularyWord,
    LessonContent,
)
from datetime import datetime

router = APIRouter(prefix="/lessons", tags=["lessons"])

# Mock data - in production this would come from database
MOCK_LESSONS: dict = {
    "lesson-1": {
        "id": "lesson-1",
        "title": "Hello & Greetings",
        "description": "Learn basic Finnish greetings and how to introduce yourself",
        "difficulty": DifficultyLevel.BEGINNER,
        "order": 1,
        "estimated_duration_minutes": 15,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "content": {
            "id": "content-1",
            "title": "Hello & Greetings",
            "description": "Basic greetings in Finnish",
            "grammar_points": ["Basic present tense", "Subject pronouns"],
            "vocabulary": [
                {
                    "finnish": "Hei",
                    "english": "Hi",
                    "part_of_speech": "interjection",
                    "pronunciation": "hay",
                    "difficulty": "beginner",
                },
                {
                    "finnish": "Terve",
                    "english": "Hello",
                    "part_of_speech": "interjection",
                    "pronunciation": "TARE-veh",
                    "difficulty": "beginner",
                },
                {
                    "finnish": "Hyvää päivää",
                    "english": "Good day",
                    "part_of_speech": "phrase",
                    "pronunciation": "HÜ-väh PAH-ee-väh",
                    "difficulty": "beginner",
                },
            ],
            "exercises": [
                {
                    "id": "ex-1",
                    "type": ExerciseType.MULTIPLE_CHOICE,
                    "question": "How do you say 'Hello' in Finnish?",
                    "options": ["Hei", "Terve", "Hyvää päivää", "Arrivederci"],
                    "correct_answer": "Terve",
                    "explanation": "Terve is a common greeting in Finnish",
                    "difficulty": DifficultyLevel.BEGINNER,
                }
            ],
        },
    },
    "lesson-2": {
        "id": "lesson-2",
        "title": "Numbers 1-10",
        "description": "Learn to count from 1 to 10 in Finnish",
        "difficulty": DifficultyLevel.BEGINNER,
        "order": 2,
        "estimated_duration_minutes": 12,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "content": {
            "id": "content-2",
            "title": "Numbers 1-10",
            "description": "Finnish numerals",
            "grammar_points": [],
            "vocabulary": [
                {"finnish": "yksi", "english": "one", "part_of_speech": "number", "difficulty": "beginner"},
                {"finnish": "kaksi", "english": "two", "part_of_speech": "number", "difficulty": "beginner"},
                {"finnish": "kolme", "english": "three", "part_of_speech": "number", "difficulty": "beginner"},
            ],
            "exercises": [],
        },
    },
}


@router.get("", response_model=List[LessonPreview])
async def get_lessons(difficulty: str = None) -> List[LessonPreview]:
    """Get list of all lessons with optional difficulty filter"""
    lessons = []
    for lesson_data in MOCK_LESSONS.values():
        if difficulty and lesson_data["difficulty"] != difficulty:
            continue
        lessons.append(
            LessonPreview(
                id=lesson_data["id"],
                title=lesson_data["title"],
                description=lesson_data["description"],
                difficulty=lesson_data["difficulty"],
                order=lesson_data["order"],
                estimated_duration_minutes=lesson_data["estimated_duration_minutes"],
            )
        )
    return sorted(lessons, key=lambda l: l.order)


@router.get("/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str) -> Lesson:
    """Get a specific lesson with all content"""
    if lesson_id not in MOCK_LESSONS:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    lesson_data = MOCK_LESSONS[lesson_id]
    return Lesson(**lesson_data)


@router.post("")
async def create_lesson(lesson: Lesson):
    """Create a new lesson (admin endpoint)"""
    # In production, validate admin status and save to database
    lesson.id = f"lesson-{len(MOCK_LESSONS) + 1}"
    lesson.created_at = datetime.utcnow()
    lesson.updated_at = datetime.utcnow()
    MOCK_LESSONS[lesson.id] = lesson.model_dump()
    return {"id": lesson.id, "status": "created"}
