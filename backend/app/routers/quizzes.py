"""
Quiz lifecycle:
  1. POST /quizzes/generate  -> AI generates questions at the student's
     recommended (or requested) difficulty for a topic.
  2. GET  /quizzes/{id}      -> student-facing quiz (no answers leaked).
  3. POST /quizzes/submit    -> grades the attempt, updates the student's
     rolling stats + topic progress, and returns per-question explanations.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.ai_content import generate_quiz_questions
from app.ml.difficulty_model import recommend_difficulty

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.post("/generate", response_model=schemas.QuizOut, status_code=201)
def generate_quiz(payload: schemas.QuizGenerateRequest, db: Session = Depends(get_db)):
    topic = db.get(models.Topic, payload.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    difficulty = payload.difficulty
    if difficulty is None:
        difficulty = "beginner"  # sensible default if called with no student context

    ai_questions = generate_quiz_questions(
        topic_title=topic.title,
        topic_summary=topic.summary,
        difficulty=difficulty,
        num_questions=payload.num_questions,
    )

    quiz = models.Quiz(
        topic_id=topic.id,
        title=f"{topic.title} — {difficulty.title()} Quiz",
        difficulty=difficulty,
        ai_generated=True,
    )
    db.add(quiz)
    db.flush()  # get quiz.id before creating child questions

    for q in ai_questions:
        db.add(models.Question(
            topic_id=topic.id,
            quiz_id=quiz.id,
            difficulty=difficulty,
            prompt=q["prompt"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_option=q["correct_option"],
            explanation=q.get("explanation", ""),
            ai_generated=True,
        ))

    db.commit()
    db.refresh(quiz)
    return quiz


@router.post("/generate-for-student", response_model=schemas.QuizOut, status_code=201)
def generate_quiz_for_student(student_id: int, topic_id: int, num_questions: int = 5,
                               db: Session = Depends(get_db)):
    """Convenience endpoint: uses the ML model to pick difficulty automatically."""
    student = db.get(models.Student, student_id)
    topic = db.get(models.Topic, topic_id)
    if not student or not topic:
        raise HTTPException(status_code=404, detail="Student or topic not found")

    rec = recommend_difficulty(
        student.avg_score, student.avg_time_per_question,
        student.quizzes_taken, student.current_streak,
    )
    return generate_quiz(schemas.QuizGenerateRequest(
        topic_id=topic_id, difficulty=rec["difficulty"], num_questions=num_questions
    ), db)


@router.get("/{quiz_id}", response_model=schemas.QuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.get(models.Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/submit", response_model=schemas.QuizResult)
def submit_quiz(payload: schemas.QuizSubmission, db: Session = Depends(get_db)):
    student = db.get(models.Student, payload.student_id)
    quiz = db.get(models.Quiz, payload.quiz_id)
    if not student or not quiz:
        raise HTTPException(status_code=404, detail="Student or quiz not found")

    questions_by_id = {q.id: q for q in quiz.questions}
    if not questions_by_id:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    attempt = models.QuizAttempt(student_id=student.id, quiz_id=quiz.id, started_at=datetime.utcnow())
    db.add(attempt)
    db.flush()

    graded = []
    correct_count = 0
    total_time = 0.0

    for ans in payload.answers:
        question = questions_by_id.get(ans.question_id)
        if not question:
            continue
        is_correct = ans.selected_option.strip().upper() == question.correct_option
        correct_count += int(is_correct)
        total_time += ans.time_taken_seconds

        db.add(models.QuizAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            selected_option=ans.selected_option.strip().upper(),
            is_correct=is_correct,
            time_taken_seconds=ans.time_taken_seconds,
        ))
        graded.append(schemas.GradedAnswer(
            question_id=question.id,
            selected_option=ans.selected_option.strip().upper(),
            correct_option=question.correct_option,
            is_correct=is_correct,
            explanation=question.explanation,
        ))

    total_questions = len(payload.answers)
    score_percent = round((correct_count / total_questions) * 100, 2) if total_questions else 0.0
    avg_time_this_attempt = round(total_time / total_questions, 2) if total_questions else 0.0

    attempt.score_percent = score_percent
    attempt.total_time_seconds = total_time
    attempt.completed_at = datetime.utcnow()

    # ---- Update rolling student stats (feeds the ML model next time) ----
    n = student.quizzes_taken
    student.avg_score = round(((student.avg_score * n) + score_percent) / (n + 1), 2)
    student.avg_time_per_question = round(((student.avg_time_per_question * n) + avg_time_this_attempt) / (n + 1), 2)
    student.quizzes_taken = n + 1
    if score_percent >= 70:
        student.current_streak += 1
    else:
        student.current_streak = 0

    # ---- Update topic mastery / progress ----
    progress = (
        db.query(models.Progress)
        .filter(models.Progress.student_id == student.id, models.Progress.topic_id == quiz.topic_id)
        .first()
    )
    if not progress:
        progress = models.Progress(student_id=student.id, topic_id=quiz.topic_id)
        db.add(progress)
        db.flush()

    m = progress.quizzes_completed
    progress.mastery_percent = round(((progress.mastery_percent * m) + score_percent) / (m + 1), 2)
    progress.quizzes_completed = m + 1
    progress.last_activity = datetime.utcnow()
    progress.completed = progress.mastery_percent >= 80

    # ---- Re-run the ML model so `current_difficulty` reflects this attempt ----
    rec = recommend_difficulty(
        student.avg_score, student.avg_time_per_question,
        student.quizzes_taken, student.current_streak,
    )
    student.current_difficulty = rec["difficulty"]
    db.add(models.PerformanceAnalysis(
        student_id=student.id,
        avg_score=student.avg_score,
        avg_time_per_question=student.avg_time_per_question,
        quizzes_taken=student.quizzes_taken,
        current_streak=student.current_streak,
        recommended_difficulty=rec["difficulty"],
        confidence=rec["confidence"],
    ))

    db.commit()

    return schemas.QuizResult(
        attempt_id=attempt.id,
        score_percent=score_percent,
        correct_count=correct_count,
        total_questions=total_questions,
        graded_answers=graded,
        updated_difficulty=student.current_difficulty,
    )
