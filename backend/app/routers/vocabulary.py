"""Vocabulary endpoints for Learning Finnish API"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models import VocabularyList, VocabularyWord, DifficultyLevel
from datetime import datetime

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])

# Mock data
MOCK_VOCABULARY_LISTS: dict = {
    "vocab-1": {
        "id": "vocab-1",
        "title": "Greetings",
        "description": "Common greetings and farewells",
        "difficulty": DifficultyLevel.BEGINNER,
        "created_at": datetime.utcnow(),
        "lesson_id": "lesson-1",
        "words": [
            {
                "id": "word-1",
                "finnish": "Hei",
                "english": "Hi",
                "part_of_speech": "interjection",
                "pronunciation": "hay",
                "example_sentence": "Hei, kuinka voit?",
                "difficulty": DifficultyLevel.BEGINNER,
            },
            {
                "id": "word-2",
                "finnish": "Terve",
                "english": "Hello",
                "part_of_speech": "interjection",
                "pronunciation": "TARE-veh",
                "example_sentence": "Terve! Minun nimeni on...",
                "difficulty": DifficultyLevel.BEGINNER,
            },
            {
                "id": "word-3",
                "finnish": "Näkemiin",
                "english": "Goodbye",
                "part_of_speech": "interjection",
                "pronunciation": "NAH-keh-mee-in",
                "example_sentence": "Näkemiin! Tervetuloa uudelleen!",
                "difficulty": DifficultyLevel.BEGINNER,
            },
        ],
    },
    "vocab-2": {
        "id": "vocab-2",
        "title": "Numbers 1-20",
        "description": "Finnish number vocabulary",
        "difficulty": DifficultyLevel.BEGINNER,
        "created_at": datetime.utcnow(),
        "lesson_id": "lesson-2",
        "words": [
            {
                "finnish": "yksi",
                "english": "one",
                "part_of_speech": "number",
                "difficulty": DifficultyLevel.BEGINNER,
            },
            {
                "finnish": "kaksi",
                "english": "two",
                "part_of_speech": "number",
                "difficulty": DifficultyLevel.BEGINNER,
            },
            {
                "finnish": "kolme",
                "english": "three",
                "part_of_speech": "number",
                "difficulty": DifficultyLevel.BEGINNER,
            },
        ],
    },
}


@router.get("", response_model=List[VocabularyList])
async def get_vocabulary_lists(difficulty: str = None) -> List[VocabularyList]:
    """Get list of all vocabulary lists"""
    lists = []
    for vocab_list in MOCK_VOCABULARY_LISTS.values():
        if difficulty and vocab_list["difficulty"] != difficulty:
            continue
        lists.append(VocabularyList(**vocab_list))
    return lists


@router.get("/{vocab_id}", response_model=VocabularyList)
async def get_vocabulary_list(vocab_id: str) -> VocabularyList:
    """Get a specific vocabulary list"""
    if vocab_id not in MOCK_VOCABULARY_LISTS:
        raise HTTPException(status_code=404, detail="Vocabulary list not found")
    
    vocab_data = MOCK_VOCABULARY_LISTS[vocab_id]
    return VocabularyList(**vocab_data)


@router.get("/lesson/{lesson_id}", response_model=List[VocabularyWord])
async def get_lesson_vocabulary(lesson_id: str) -> List[VocabularyWord]:
    """Get vocabulary for a specific lesson"""
    words = []
    for vocab_list in MOCK_VOCABULARY_LISTS.values():
        if vocab_list.get("lesson_id") == lesson_id:
            words.extend(vocab_list["words"])
    return words


@router.post("")
async def create_vocabulary_list(vocab_list: VocabularyList):
    """Create a new vocabulary list (admin endpoint)"""
    vocab_list.id = f"vocab-{len(MOCK_VOCABULARY_LISTS) + 1}"
    vocab_list.created_at = datetime.utcnow()
    MOCK_VOCABULARY_LISTS[vocab_list.id] = vocab_list.model_dump()
    return {"id": vocab_list.id, "status": "created"}
