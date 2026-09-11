"""
Inference wrapper around the trained difficulty-recommendation model.
Loads app/ml/difficulty_model.pkl (built by train_model.py) once at import
time and exposes a single `recommend_difficulty()` function used by the API.
"""
import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "difficulty_model.pkl")

_bundle = None


def _load():
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            # Auto-bootstrap on first run so the API doesn't hard-fail if
            # `python -m app.ml.train_model` hasn't been run yet.
            from app.ml.train_model import train_and_save
            train_and_save()
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def recommend_difficulty(avg_score: float, avg_time_per_question: float,
                          quizzes_taken: int, current_streak: int) -> dict:
    """
    Returns {"difficulty": "beginner"|"intermediate"|"advanced", "confidence": float}
    """
    bundle = _load()
    clf = bundle["model"]
    feature_cols = bundle["feature_cols"]

    features = np.array([[avg_score, avg_time_per_question, quizzes_taken, current_streak]])
    proba = clf.predict_proba(features)[0]
    classes = clf.classes_

    best_idx = int(np.argmax(proba))
    return {
        "difficulty": classes[best_idx],
        "confidence": float(proba[best_idx]),
        "feature_cols": feature_cols,
    }
