# AI-Powered E-Learning & Adaptive Learning Platform

Full-stack platform that personalizes each student's learning path based on
their performance, instead of serving static course content.

**Stack:** Python · FastAPI · PostgreSQL · SQLAlchemy · Next.js · JavaScript ·
Tailwind CSS · scikit-learn (ML) · Cloudinary

```
elearning-platform/
├── backend/     FastAPI + PostgreSQL + SQLAlchemy API, ML model, AI content generation
└── frontend/    Next.js + Tailwind CSS client
```

## What's implemented

- **Full REST API** (FastAPI) — student management, courses/topics, quizzes,
  progress tracking, and performance analysis. See `backend/README.md` for the
  full endpoint table.
- **ML difficulty-recommendation model** (scikit-learn `RandomForestClassifier`)
  that takes a student's rolling avg score, avg time/question, quizzes taken,
  and streak, and predicts beginner / intermediate / advanced. Every quiz
  submission updates the student's stats, re-runs the model, and the *next*
  quiz is generated at that recommended level — this is the adaptive loop.
- **AI-generated content** — quiz questions, multiple-choice options, and
  per-question explanations, plus short study notes per topic, via the OpenAI
  API (`app/services/ai_content.py`). Falls back to a deterministic template
  generator automatically if no `OPENAI_API_KEY` is set, so the app still runs
  end-to-end without external services.
- **Cloudinary integration** for learning-material uploads (PDFs, slides,
  videos, images) — files go to Cloudinary, only the URL + metadata are
  persisted in PostgreSQL for fast retrieval.
- **Next.js + Tailwind frontend** — auth, dashboard with a mastery chart and
  live difficulty recommendation, course/topic browsing, material upload, and
  a full quiz-taking flow with graded results and explanations.

## Quick start

1. **Backend** — see `backend/README.md`. Short version:
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env   # fill in DATABASE_URL, CLOUDINARY_*, (optional) OPENAI_API_KEY
   python -m app.ml.train_model
   python -m app.seed
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend** — see `frontend/README.md`. Short version:
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   npm run dev
   ```
3. Open http://localhost:3000, sign in with `demo@student.com` / `demo1234`
   (from the seed script), and walk through: Courses → a Topic → Start quiz →
   Submit → Dashboard (watch the difficulty/mastery update).
