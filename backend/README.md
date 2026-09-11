# Adaptive E-Learning Platform — Backend

FastAPI + PostgreSQL + SQLAlchemy backend with a scikit-learn difficulty-recommendation
model and AI-generated quiz/practice content.

## 1. Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then edit .env with your real values
```

You'll need:
- A running PostgreSQL instance and a database matching `DATABASE_URL` in `.env`.
- A [Cloudinary](https://cloudinary.com) account (free tier is fine) for `CLOUDINARY_*` vars.
- (Optional) An `OPENAI_API_KEY` for real AI-generated quizzes/notes. Without it,
  the platform automatically falls back to a template-based generator so
  everything still runs end-to-end for demos/grading.

## 2. Train the ML model (bootstrap)

```bash
python -m app.ml.train_model
```

This generates a synthetic-but-pedagogically-sensible training set and saves
`app/ml/difficulty_model.pkl`. The API will also auto-bootstrap this on first
request if you skip this step. Once real quiz-attempt data accumulates,
call `retrain_from_db()` (in `app/ml/train_model.py`) to retrain on real
student behavior instead of the synthetic bootstrap.

## 3. Seed demo data (optional but recommended)

```bash
python -m app.seed
```

Creates one demo course with 3 topics and a demo student
(`demo@student.com` / `demo1234`).

## 4. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs

## API overview

| Area | Endpoints |
|---|---|
| Students | `POST /students/register`, `POST /students/login`, `GET /students`, `GET /students/{id}` |
| Courses/Topics | `POST /courses`, `GET /courses`, `GET /courses/{id}`, `POST /courses/{id}/topics`, `GET /courses/{id}/topics` |
| Topics | `GET /topics/{id}`, `GET /topics/{id}/materials`, `GET /topics/{id}/practice-notes?difficulty=` |
| Materials | `POST /materials/upload` (multipart, uploads to Cloudinary), `DELETE /materials/{id}` |
| Quizzes | `POST /quizzes/generate`, `POST /quizzes/generate-for-student` (uses ML recommendation), `GET /quizzes/{id}`, `POST /quizzes/submit` |
| Progress | `GET /progress/{student_id}`, `GET /progress/{student_id}/summary` |
| Analysis (ML) | `GET /analysis/{student_id}/recommend-difficulty`, `GET /analysis/{student_id}/history` |

## How the adaptive loop works

1. Student takes a quiz → `POST /quizzes/submit`.
2. The endpoint updates the student's rolling stats (`avg_score`,
   `avg_time_per_question`, `quizzes_taken`, `current_streak`) and topic
   `Progress.mastery_percent`.
3. It re-runs the trained model (`app/ml/difficulty_model.py`) on the updated
   stats and stores the recommendation in `PerformanceAnalysis` plus the
   student's `current_difficulty`.
4. The next quiz for that student (`POST /quizzes/generate-for-student`) asks
   the AI content service for questions at that recommended difficulty —
   closing the loop from performance data to content delivery.

## Schema migrations

`Base.metadata.create_all()` (used in `main.py`/`seed.py`) is fine for local
dev and grading. For a real deployment, initialize Alembic instead:

```bash
alembic init migrations
# edit migrations/env.py to import Base from app.database and app.models
alembic revision --autogenerate -m "init"
alembic upgrade head
```
