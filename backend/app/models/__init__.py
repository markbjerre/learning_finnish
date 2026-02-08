"""Data models for Learning Finnish API"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels for lessons"""
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseType(str, Enum):
    """Types of exercises"""
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    TRANSLATION = "translation"
    LISTENING = "listening"
    SPEAKING = "speaking"


class WordStatus(str, Enum):
    """Word status for user vocabulary tracking"""
    RECENT = "recent"
    LEARNING = "learning"
    MASTERED = "mastered"


# Vocabulary Models
class VocabularyWord(BaseModel):
    """A single vocabulary word"""
    id: Optional[str] = None
    finnish: str
    english: str
    part_of_speech: str  # noun, verb, adjective, etc.
    example_sentence: Optional[str] = None
    pronunciation: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER


class VocabularyList(BaseModel):
    """A collection of vocabulary words"""
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    words: List[VocabularyWord]
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    created_at: Optional[datetime] = None
    lesson_id: Optional[str] = None


# Exercise Models
class Exercise(BaseModel):
    """An exercise within a lesson"""
    id: Optional[str] = None
    type: ExerciseType
    question: str
    options: List[str]  # For multiple choice
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: DifficultyLevel


class LessonContent(BaseModel):
    """Content for a lesson"""
    id: Optional[str] = None
    title: str
    description: str
    grammar_points: List[str]
    vocabulary: List[VocabularyWord]
    exercises: List[Exercise]


# Lesson Models
class Lesson(BaseModel):
    """A learning lesson"""
    id: Optional[str] = None
    title: str
    description: str
    difficulty: DifficultyLevel
    order: int
    content: LessonContent
    estimated_duration_minutes: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LessonPreview(BaseModel):
    """Preview of a lesson (without full content)"""
    id: Optional[str] = None
    title: str
    description: str
    difficulty: DifficultyLevel
    order: int
    estimated_duration_minutes: int


# Progress Models
class ExerciseResult(BaseModel):
    """Result of a completed exercise"""
    exercise_id: str
    correct: bool
    user_answer: str
    time_spent_seconds: int


class LessonProgress(BaseModel):
    """Progress tracking for a lesson"""
    id: Optional[str] = None
    user_id: str
    lesson_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    exercises_completed: int
    exercises_correct: int
    time_spent_seconds: int
    status: str = "in_progress"  # in_progress, completed, abandoned


class UserProgress(BaseModel):
    """Overall progress for a user"""
    user_id: str
    total_lessons_completed: int
    total_exercises_completed: int
    total_accuracy: float  # 0-100
    current_difficulty: DifficultyLevel
    total_study_time_minutes: int
    last_studied: Optional[datetime] = None
    streak_days: int = 0


# API Response Models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime


class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime


# Word and Dictionary Models
class GrammaticalForm(BaseModel):
    """Grammatical form of a word"""
    case: str  # nominative, genitive, partitive, etc.
    finnish: str
    english: str


class ExampleSentence(BaseModel):
    """Example sentence for a word"""
    finnish: str
    english: str


class Word(BaseModel):
    """Dictionary word with full metadata"""
    id: Optional[str] = None
    finnish_word: str
    english_translation: str
    part_of_speech: str
    grammatical_forms: Optional[List[GrammaticalForm]] = None
    example_sentences: Optional[List[ExampleSentence]] = None
    ai_definition: Optional[str] = None
    ai_examples: Optional[List[ExampleSentence]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WordSearchResult(BaseModel):
    """Result of word search operation"""
    id: Optional[str] = None
    finnish_word: str
    english_translation: str
    part_of_speech: str
    grammatical_forms: Optional[List[GrammaticalForm]] = None
    example_sentences: Optional[List[ExampleSentence]] = None
    ai_definition: Optional[str] = None


class UserWord(BaseModel):
    """User's saved word with learning progress"""
    id: Optional[str] = None
    user_id: str
    word_id: str
    word: Optional[Word] = None  # Nested word data
    status: WordStatus = WordStatus.RECENT
    proficiency: int = 0  # 0-100 scale
    date_added: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    review_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SaveWordRequest(BaseModel):
    """Request to save a word to user's wordbook"""
    finnish_word: str
    user_id: str


class UpdateWordStatusRequest(BaseModel):
    """Request to update word status"""
    status: WordStatus
    proficiency: Optional[int] = None


class AIDefinitionRequest(BaseModel):
    """Request for AI-generated word definition"""
    finnish_word: str
    context: Optional[str] = None
