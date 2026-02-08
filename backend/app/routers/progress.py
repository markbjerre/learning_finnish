"""Progress tracking endpoints for Learning Finnish API"""

from fastapi import APIRouter, HTTPException, Body
from typing import List
from app.models import LessonProgress, UserProgress, ExerciseResult
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/progress", tags=["progress"])

# Mock data
MOCK_PROGRESS: dict = {}
MOCK_USER_STATS: dict = {
    "user-1": {
        "user_id": "user-1",
        "total_lessons_completed": 2,
        "total_exercises_completed": 5,
        "total_accuracy": 80.0,
        "current_difficulty": "beginner",
        "total_study_time_minutes": 45,
        "last_studied": datetime.utcnow(),
        "streak_days": 3,
    }
}


class ExerciseResultRequest(BaseModel):
    """Request model for submitting exercise results"""
    exercise_id: str
    correct: bool
    user_answer: str
    time_spent_seconds: int


@router.post("/lessons/{lesson_id}/start")
async def start_lesson(lesson_id: str, user_id: str = "user-1"):
    """Mark the beginning of a lesson"""
    progress_id = f"progress-{lesson_id}-{user_id}"
    progress = {
        "id": progress_id,
        "user_id": user_id,
        "lesson_id": lesson_id,
        "started_at": datetime.utcnow(),
        "completed_at": None,
        "exercises_completed": 0,
        "exercises_correct": 0,
        "time_spent_seconds": 0,
        "status": "in_progress",
    }
    MOCK_PROGRESS[progress_id] = progress
    return progress


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: str, user_id: str = "user-1"):
    """Mark a lesson as completed"""
    progress_id = f"progress-{lesson_id}-{user_id}"
    if progress_id not in MOCK_PROGRESS:
        raise HTTPException(status_code=404, detail="Lesson progress not found")
    
    progress = MOCK_PROGRESS[progress_id]
    progress["completed_at"] = datetime.utcnow()
    progress["status"] = "completed"
    
    # Update user stats
    if user_id in MOCK_USER_STATS:
        MOCK_USER_STATS[user_id]["total_lessons_completed"] += 1
    
    return progress


@router.post("/exercises/{exercise_id}/submit")
async def submit_exercise_result(
    exercise_id: str,
    result: ExerciseResultRequest = Body(...),
    user_id: str = "user-1"
):
    """Submit exercise result and track progress"""
    # In production, validate the answer and calculate score
    return {
        "exercise_id": exercise_id,
        "user_id": user_id,
        "correct": result.correct,
        "feedback": "Correct!" if result.correct else "Incorrect. Try again!",
        "recorded_at": datetime.utcnow(),
    }


@router.get("/user/{user_id}", response_model=UserProgress)
async def get_user_progress(user_id: str) -> UserProgress:
    """Get overall progress for a user"""
    if user_id not in MOCK_USER_STATS:
        # Return default stats for new user
        return UserProgress(
            user_id=user_id,
            total_lessons_completed=0,
            total_exercises_completed=0,
            total_accuracy=0.0,
            current_difficulty="beginner",
            total_study_time_minutes=0,
            last_studied=None,
            streak_days=0,
        )
    
    stats = MOCK_USER_STATS[user_id]
    return UserProgress(**stats)


@router.get("/lessons/{lesson_id}/user/{user_id}", response_model=LessonProgress)
async def get_lesson_progress(lesson_id: str, user_id: str) -> LessonProgress:
    """Get progress for a specific lesson"""
    progress_id = f"progress-{lesson_id}-{user_id}"
    if progress_id not in MOCK_PROGRESS:
        raise HTTPException(status_code=404, detail="Lesson progress not found")
    
    progress_data = MOCK_PROGRESS[progress_id]
    return LessonProgress(**progress_data)


@router.post("/reset/{user_id}")
async def reset_user_progress(user_id: str):
    """Reset all progress for a user (admin endpoint)"""
    # Remove all progress entries for this user
    keys_to_remove = [
        k for k in MOCK_PROGRESS.keys() if f"-{user_id}" in k
    ]
    for key in keys_to_remove:
        del MOCK_PROGRESS[key]
    
    if user_id in MOCK_USER_STATS:
        del MOCK_USER_STATS[user_id]
    
    return {"status": "reset", "user_id": user_id}
