"""SQLAlchemy database models for Learning Finnish"""

import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base, APP_SCHEMA
from datetime import datetime
import enum

# PostgreSQL: use app schema to avoid conflict with homelab public.words (integer id)
# SQLite: no schema (SQLite has limited schema support)
def _table_args():
    from app.config import settings
    if (settings.database_url or "").startswith("postgresql"):
        return {"schema": APP_SCHEMA}
    return {}


def _fk(table_col: str) -> str:
    """Return schema-qualified FK for PostgreSQL so cross-table refs resolve."""
    from app.config import settings
    if (settings.database_url or "").startswith("postgresql"):
        return f"{APP_SCHEMA}.{table_col}"
    return table_col


TABLE_ARGS = _table_args()


class DifficultyEnum(str, enum.Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseTypeEnum(str, enum.Enum):
    """Exercise types"""
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    TRANSLATION = "translation"
    LISTENING = "listening"
    SPEAKING = "speaking"


class WordStatusEnum(str, enum.Enum):
    """Word status for user vocabulary tracking"""
    RECENT = "recent"
    LEARNING = "learning"
    MASTERED = "mastered"


class Lesson(Base):
    """Lesson model"""
    __tablename__ = "lessons"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text)
    difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.BEGINNER, index=True)
    order = Column(Integer, unique=True, index=True)
    estimated_duration_minutes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    vocabulary_lists = relationship("VocabularyList", back_populates="lesson", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan")
    progress_entries = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")


class VocabularyList(Base):
    """Collection of vocabulary words"""
    __tablename__ = "vocabulary_lists"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text)
    difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.BEGINNER)
    lesson_id = Column(String, ForeignKey(_fk("lessons.id")), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lesson = relationship("Lesson", back_populates="vocabulary_lists")
    words = relationship("VocabularyWord", back_populates="vocabulary_list", cascade="all, delete-orphan")


class VocabularyWord(Base):
    """Individual vocabulary word"""
    __tablename__ = "vocabulary_words"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    finnish = Column(String(255), index=True)
    english = Column(String(255), index=True)
    part_of_speech = Column(String(100))
    example_sentence = Column(Text)
    pronunciation = Column(String(255))
    difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.BEGINNER)
    vocabulary_list_id = Column(String, ForeignKey(_fk("vocabulary_lists.id")), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    vocabulary_list = relationship("VocabularyList", back_populates="words")


class Exercise(Base):
    """Exercise within a lesson"""
    __tablename__ = "exercises"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    lesson_id = Column(String, ForeignKey(_fk("lessons.id")), index=True)
    type = Column(SQLEnum(ExerciseTypeEnum), index=True)
    question = Column(Text)
    options = Column(Text)  # JSON string
    correct_answer = Column(String(255))
    explanation = Column(Text)
    difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.BEGINNER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lesson = relationship("Lesson", back_populates="exercises")
    results = relationship("ExerciseResult", back_populates="exercise", cascade="all, delete-orphan")


class User(Base):
    """User profile"""
    __tablename__ = "users"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    progress_entries = relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    exercise_results = relationship("ExerciseResult", back_populates="user", cascade="all, delete-orphan")
    user_words = relationship("UserWord", back_populates="user", cascade="all, delete-orphan")


class LessonProgress(Base):
    """Track user progress in lessons"""
    __tablename__ = "lesson_progress"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey(_fk("users.id")), index=True)
    lesson_id = Column(String, ForeignKey(_fk("lessons.id")), index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    exercises_completed = Column(Integer, default=0)
    exercises_correct = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, default=0)
    status = Column(String(50), default="in_progress", index=True)  # in_progress, completed, abandoned

    # Relationships
    user = relationship("User", back_populates="progress_entries")
    lesson = relationship("Lesson", back_populates="progress_entries")


class ExerciseResult(Base):
    """Result of a completed exercise"""
    __tablename__ = "exercise_results"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey(_fk("users.id")), index=True)
    exercise_id = Column(String, ForeignKey(_fk("exercises.id")), index=True)
    lesson_progress_id = Column(String, ForeignKey(_fk("lesson_progress.id")), index=True)
    correct = Column(Boolean, index=True)
    user_answer = Column(Text)
    time_spent_seconds = Column(Integer)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="exercise_results")
    exercise = relationship("Exercise", back_populates="results")


class Word(Base):
    """Dictionary word with metadata"""
    __tablename__ = "words"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    finnish_word = Column(String(255), index=True, unique=True)
    english_translation = Column(String(255), index=True)
    part_of_speech = Column(String(100))  # noun, verb, adjective, etc.
    grammatical_forms = Column(Text)  # JSON: nominative, genitive, partitive, etc.
    example_sentences = Column(Text)  # JSON: list of example sentences with translations
    ai_definition = Column(Text, nullable=True)  # AI-generated definition
    ai_examples = Column(Text, nullable=True)  # JSON: AI-generated examples
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Spaced repetition fields
    danish_translation = Column(String(255), nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    priority = Column(Float, default=1.0, index=True)
    times_served = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    last_score = Column(Float, nullable=True)
    last_served = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user_words = relationship("UserWord", back_populates="word", cascade="all, delete-orphan")
    inflections = relationship("Inflection", back_populates="word", cascade="all, delete-orphan")
    verb_forms = relationship("VerbForm", back_populates="word", cascade="all, delete-orphan")


class UserWord(Base):
    """Track user's word learning progress"""
    __tablename__ = "user_words"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey(_fk("users.id")), index=True)
    word_id = Column(String, ForeignKey(_fk("words.id")), index=True)
    status = Column(SQLEnum(WordStatusEnum), default=WordStatusEnum.RECENT, index=True)
    proficiency = Column(Integer, default=0)  # 0-100 scale
    date_added = Column(DateTime(timezone=True), server_default=func.now())
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_words")
    word = relationship("Word", back_populates="user_words")


class Inflection(Base):
    """Finnish noun/adjective inflections by case"""
    __tablename__ = "inflections"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    word_id = Column(String, ForeignKey(_fk("words.id"), ondelete="CASCADE"), index=True)
    case_name = Column(String(100), nullable=False)
    singular = Column(String(255), nullable=True)
    plural = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    word = relationship("Word", back_populates="inflections")


class VerbForm(Base):
    """Finnish verb conjugations"""
    __tablename__ = "verb_forms"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    word_id = Column(String, ForeignKey(_fk("words.id"), ondelete="CASCADE"), index=True)
    form_name = Column(String(100), nullable=False)
    form_value = Column(String(255), nullable=False)
    tense = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

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

    word_id = Column(String, ForeignKey(_fk("words.id"), ondelete="CASCADE"), primary_key=True)
    concept_id = Column(String, ForeignKey(_fk("concepts.id"), ondelete="CASCADE"), primary_key=True)


class SpacedExerciseLog(Base):
    """Log of spaced repetition exercises"""
    __tablename__ = "spaced_exercise_log"
    __table_args__ = TABLE_ARGS

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    exercise_type = Column(String(100), nullable=False)
    level_used = Column(Integer, nullable=True)
    words_used = Column(Text, nullable=True)  # JSON array of word IDs
    concepts_used = Column(Text, nullable=True)  # JSON array of concept IDs
    prompt_sent = Column(Text, nullable=True)
    user_response = Column(Text, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    word_scores = Column(Text, nullable=True)  # JSON
    concept_scores = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AppSetting(Base):
    """System settings (level, preferences)"""
    __tablename__ = "app_settings"
    __table_args__ = TABLE_ARGS

    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)  # JSON value
