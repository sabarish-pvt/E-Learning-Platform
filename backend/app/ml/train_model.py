"""
Trains the difficulty-recommendation model.

The model predicts which difficulty level (beginner / intermediate / advanced)
a student should be served next, based on four rolling features:
  - avg_score               (0-100, recent average quiz score)
  - avg_time_per_question   (seconds, recent average time per question)
  - quizzes_taken           (total quizzes completed so far)
  - current_streak          (consecutive correct answers)

In production this would train on real historical (features -> next_difficulty)
pairs pulled from the `quiz_attempts` / `performance_analyses` tables. Since no
labeled history exists on day one, we bootstrap with a synthetic dataset built
from pedagogically sensible rules (high score + fast + long streak -> harder;
low score + slow + short streak -> easier), plus noise, so the model has a
sane cold-start policy. Call `retrain_from_db()` periodically once real
attempt data accumulates to replace this bootstrap model with one learned
from actual student behavior.

Run directly to (re)build the bootstrap model:
    python -m app.ml.train_model
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "difficulty_model.pkl")
LABELS = ["beginner", "intermediate", "advanced"]


def _label_from_rules(avg_score, avg_time, quizzes_taken, streak, rng):
    """Ground-truth heuristic used only to generate synthetic training labels."""
    score_component = avg_score / 100.0
    time_component = 1.0 - min(avg_time / 60.0, 1.0)  # faster -> higher
    streak_component = min(streak / 10.0, 1.0)
    experience_component = min(quizzes_taken / 20.0, 1.0)

    composite = (
        0.5 * score_component
        + 0.2 * time_component
        + 0.2 * streak_component
        + 0.1 * experience_component
    )
    composite += rng.normal(0, 0.05)  # noise so the model doesn't memorize a hard threshold

    if composite < 0.45:
        return "beginner"
    elif composite < 0.75:
        return "intermediate"
    return "advanced"


def generate_synthetic_dataset(n_samples: int = 4000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    avg_score = np.clip(rng.normal(65, 20, n_samples), 0, 100)
    avg_time = np.clip(rng.normal(30, 15, n_samples), 3, 120)
    quizzes_taken = rng.integers(0, 40, n_samples)
    streak = np.clip(rng.normal(3, 3, n_samples).round(), 0, 20).astype(int)

    labels = [
        _label_from_rules(s, t, q, st, rng)
        for s, t, q, st in zip(avg_score, avg_time, quizzes_taken, streak)
    ]

    return pd.DataFrame({
        "avg_score": avg_score,
        "avg_time_per_question": avg_time,
        "quizzes_taken": quizzes_taken,
        "current_streak": streak,
        "difficulty": labels,
    })


def train_and_save(df: pd.DataFrame = None, model_path: str = MODEL_PATH) -> dict:
    if df is None:
        df = generate_synthetic_dataset()

    feature_cols = ["avg_score", "avg_time_per_question", "quizzes_taken", "current_streak"]
    X = df[feature_cols]
    y = df["difficulty"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)

    joblib.dump({"model": clf, "feature_cols": feature_cols, "labels": LABELS}, model_path)
    return report


def retrain_from_db():
    """
    Rebuilds the model from real accumulated data instead of the synthetic
    bootstrap set. Intended to be called periodically (e.g. a nightly cron /
    scheduled task) once enough attempts exist.
    """
    from app.database import SessionLocal
    from app.models import PerformanceAnalysis

    db = SessionLocal()
    try:
        rows = db.query(PerformanceAnalysis).all()
        if len(rows) < 200:
            print(f"Only {len(rows)} labeled rows available; keeping synthetic bootstrap model.")
            return
        df = pd.DataFrame([{
            "avg_score": r.avg_score,
            "avg_time_per_question": r.avg_time_per_question,
            "quizzes_taken": r.quizzes_taken,
            "current_streak": r.current_streak,
            "difficulty": r.recommended_difficulty.value,
        } for r in rows])
        report = train_and_save(df)
        print("Retrained on real data:", report["accuracy"])
    finally:
        db.close()


if __name__ == "__main__":
    report = train_and_save()
    print(f"Model trained and saved to {MODEL_PATH}")
    print(f"Test accuracy: {report['accuracy']:.3f}")
