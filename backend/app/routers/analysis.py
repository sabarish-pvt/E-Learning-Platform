"""
Performance analysis: runs the trained ML model against a student's rolling
stats to recommend the difficulty level they should be served next, and logs
the recommendation for auditability / future retraining.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.ml.difficulty_model import recommend_difficulty

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{student_id}/recommend-difficulty", response_model=schemas.DifficultyRecommendation)
def recommend(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = recommend_difficulty(
        avg_score=student.avg_score,
        avg_time_per_question=student.avg_time_per_question,
        quizzes_taken=student.quizzes_taken,
        current_streak=student.current_streak,
    )

    analysis = models.PerformanceAnalysis(
        student_id=student_id,
        avg_score=student.avg_score,
        avg_time_per_question=student.avg_time_per_question,
        quizzes_taken=student.quizzes_taken,
        current_streak=student.current_streak,
        recommended_difficulty=result["difficulty"],
        confidence=result["confidence"],
    )
    db.add(analysis)

    # Close the loop: persist the recommendation as the student's active difficulty
    # so the next quiz/content generation call uses it automatically.
    student.current_difficulty = result["difficulty"]
    db.commit()

    return {
        "student_id": student_id,
        "recommended_difficulty": result["difficulty"],
        "confidence": result["confidence"],
        "features_used": {
            "avg_score": student.avg_score,
            "avg_time_per_question": student.avg_time_per_question,
            "quizzes_taken": student.quizzes_taken,
            "current_streak": student.current_streak,
        },
    }


@router.get("/{student_id}/history")
def analysis_history(student_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(models.PerformanceAnalysis)
        .filter(models.PerformanceAnalysis.student_id == student_id)
        .order_by(models.PerformanceAnalysis.created_at.desc())
        .all()
    )
    return [
        {
            "created_at": r.created_at,
            "avg_score": r.avg_score,
            "recommended_difficulty": r.recommended_difficulty,
            "confidence": r.confidence,
        }
        for r in rows
    ]
