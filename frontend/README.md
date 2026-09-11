# Adaptive E-Learning Platform — Frontend

Next.js (App Router, JavaScript) + Tailwind CSS client for the adaptive
e-learning platform.

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local     # point NEXT_PUBLIC_API_URL at your backend
npm run dev
```

Visit http://localhost:3000. Make sure the FastAPI backend is running at the
URL configured in `.env.local` (default `http://localhost:8000`).

## Pages

| Route | Purpose |
|---|---|
| `/` | Sign in / register |
| `/dashboard` | Stats, ML-recommended difficulty, topic mastery chart |
| `/courses` | Browse courses |
| `/courses/[id]` | Topics within a course |
| `/topics/[id]` | AI study notes, Cloudinary material upload/list, start adaptive quiz |
| `/quiz/[id]` | Take an AI-generated quiz, submit, see graded results + AI explanations |

## Notes

- Auth is a simple JWT stored in `localStorage` via `context/AuthContext.jsx` —
  fine for an internship/demo project; swap for httpOnly cookies for production.
- `lib/api.js` is the single place that talks to the backend; every page goes
  through it.
- Tailwind utility classes are composed into a few reusable classes
  (`.card`, `.btn-primary`, `.btn-secondary`, `.badge`) in `app/globals.css`.
