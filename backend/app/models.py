"""
SQLAlchemy ORM models for the adaptive e-learning platform.

Core entities:
- Student: learner account + rolling performance stats used by the ML model
- Course / Topic: content hierarchy
- LearningMaterial: Cloudinary-hosted files (PDF/video/slides) attached to a topic
- Question / Quiz: AI-generatable practice/assessment content
- QuizAttempt / QuizAnswer: a student's attempt at a quiz, with per-question answers
- PerformanceAnalysis: snapshots produced by the ML difficulty-recommendation engine
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship

from app.database import Base


class DifficultyLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Rolling stats maintained after every quiz submission; these are the
    # features the ML model consumes to recommend a difficulty level.
    avg_score = Column(Float, default=0.0)          # 0-100
    avg_time_per_question = Column(Float, default=0.0)  # seconds
    quizzes_taken = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)     # consecutive correct answers
    current_difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.beginner)

    progress_records = relationship("Progress", back_populates="student", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="student", cascade="all, delete-orphan")
    analyses = relationship("PerformanceAnalysis", back_populates="student", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    subject = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    topics = relationship("Topic", back_populates="course", cascade="all, delete-orphan", order_by="Topic.order_index")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, default="")
    order_index = Column(Integer, default=0)

    course = relationship("Course", back_populates="topics")
    materials = relationship("LearningMaterial", back_populates="topic", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="topic", cascade="all, delete-orphan")


class LearningMaterial(Base):
    """A file (PDF, slide deck, video, image) uploaded to Cloudinary for a topic."""
    __tablename__ = "learning_materials"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(200), nullable=False)
    resource_type = Column(String(30), default="raw")   # image | video | raw
    cloudinary_public_id = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    format = Column(String(20), default="")
    bytes = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("Topic", back_populates="materials")


class Question(Base):
    """A single question, either AI-generated or authored manually."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=True)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.beginner)
    prompt = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    correct_option = Column(String(1), nullable=False)  # 'A' | 'B' | 'C' | 'D'
    explanation = Column(Text, default="")               # AI-generated explanation
    ai_generated = Column(Boolean, default=False)

    topic = relationship("Topic", back_populates="questions")
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("QuizAnswer", back_populates="question")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(200), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.beginner)
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score_percent = Column(Float, default=0.0)
    total_time_seconds = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="attempts")
    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option = Column(String(1), nullable=False)
    is_correct = Column(Boolean, default=False)
    time_taken_seconds = Column(Float, default=0.0)

    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")


class Progress(Base):
    """Per-student, per-topic mastery tracking."""
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    mastery_percent = Column(Float, default=0.0)   # 0-100
    quizzes_completed = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)

    student = relationship("Student", back_populates="progress_records")
    topic = relationship("Topic", back_populates="progress_records")


class PerformanceAnalysis(Base):
    """
    Snapshot produced whenever the ML model evaluates a student.
    Stores the input features and the recommended difficulty, so the
    recommendation history is auditable.
    """
    __tablename__ = "performance_analyses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    avg_score = Column(Float)
    avg_time_per_question = Column(Float)
    quizzes_taken = Column(Integer)
    current_streak = Column(Integer)
    recommended_difficulty = Column(Enum(DifficultyLevel))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="analyses")
