"""
Progress tracking: per-student, per-topic mastery, and an overall dashboard summary.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{student_id}", response_model=list[schemas.ProgressOut])
def get_progress(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db.query(models.Progress).filter(models.Progress.student_id == student_id).all()


@router.get("/{student_id}/summary")
def get_progress_summary(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    records = db.query(models.Progress).filter(models.Progress.student_id == student_id).all()
    topics_started = len(records)
    topics_completed = sum(1 for r in records if r.completed)
    overall_mastery = round(sum(r.mastery_percent for r in records) / topics_started, 2) if topics_started else 0.0

    return {
        "student_id": student_id,
        "current_difficulty": student.current_difficulty,
        "avg_score": student.avg_score,
        "quizzes_taken": student.quizzes_taken,
        "current_streak": student.current_streak,
        "topics_started": topics_started,
        "topics_completed": topics_completed,
        "overall_mastery_percent": overall_mastery,
    }
