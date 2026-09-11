"""
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000

Interactive API docs will be at http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app import models  # noqa: F401  (ensures models are registered on Base before create_all)
from app.routers import students, courses, topics, quizzes, progress, analysis, uploads

# Creates tables if they don't exist yet. For real schema evolution over time,
# switch to Alembic migrations (see README) instead of relying on create_all.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Adaptive E-Learning Platform API",
    description=(
        "REST API for student management, courses/topics, AI-generated quizzes "
        "and study material, progress tracking, and ML-driven difficulty "
        "recommendation."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(courses.router)
app.include_router(topics.router)
app.include_router(quizzes.router)
app.include_router(progress.router)
app.include_router(analysis.router)
app.include_router(uploads.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "adaptive-elearning-api"}
