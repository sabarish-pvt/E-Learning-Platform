"""
Pydantic schemas used for request validation and response serialization.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import DifficultyLevel


# ---------- Student ----------
class StudentCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    avg_score: float
    avg_time_per_question: float
    quizzes_taken: int
    current_streak: int
    current_difficulty: DifficultyLevel
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student: StudentOut


# ---------- Course / Topic ----------
class CourseCreate(BaseModel):
    title: str
    description: str = ""
    subject: str = ""


class TopicCreate(BaseModel):
    title: str
    summary: str = ""
    order_index: int = 0


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_id: int
    title: str
    summary: str
    order_index: int


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    subject: str
    created_at: datetime
    topics: List[TopicOut] = []


# ---------- Learning material ----------
class LearningMaterialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: int
    title: str
    resource_type: str
    url: str
    format: str
    bytes: int
    uploaded_at: datetime


# ---------- Questions / Quizzes ----------
class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    prompt: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: DifficultyLevel
    ai_generated: bool
    # NOTE: correct_option / explanation intentionally excluded from the
    # student-facing schema so the answer isn't leaked before submission.


class QuestionWithAnswer(QuestionOut):
    correct_option: str
    explanation: str


class QuizOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: int
    title: str
    difficulty: DifficultyLevel
    ai_generated: bool
    created_at: datetime
    questions: List[QuestionOut] = []


class QuizGenerateRequest(BaseModel):
    topic_id: int
    difficulty: Optional[DifficultyLevel] = None  # if omitted, ML recommendation is used
    num_questions: int = 5


# ---------- Quiz submission ----------
class AnswerSubmission(BaseModel):
    question_id: int
    selected_option: str
    time_taken_seconds: float = 0.0


class QuizSubmission(BaseModel):
    student_id: int
    quiz_id: int
    answers: List[AnswerSubmission]


class GradedAnswer(BaseModel):
    question_id: int
    selected_option: str
    correct_option: str
    is_correct: bool
    explanation: str


class QuizResult(BaseModel):
    attempt_id: int
    score_percent: float
    correct_count: int
    total_questions: int
    graded_answers: List[GradedAnswer]
    updated_difficulty: DifficultyLevel


# ---------- Progress ----------
class ProgressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: int
    mastery_percent: float
    quizzes_completed: int
    completed: bool
    last_activity: datetime


# ---------- Performance analysis / ML ----------
class DifficultyRecommendation(BaseModel):
    student_id: int
    recommended_difficulty: DifficultyLevel
    confidence: float
    features_used: dict
