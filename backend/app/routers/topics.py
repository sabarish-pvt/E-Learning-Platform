"""
Topic detail retrieval and AI-generated practice/study material for a topic.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.ai_content import generate_practice_material

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/{topic_id}", response_model=schemas.TopicOut)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.get(models.Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.get("/{topic_id}/materials", response_model=list[schemas.LearningMaterialOut])
def list_materials(topic_id: int, db: Session = Depends(get_db)):
    return db.query(models.LearningMaterial).filter(models.LearningMaterial.topic_id == topic_id).all()


@router.get("/{topic_id}/practice-notes")
def get_practice_notes(
    topic_id: int,
    difficulty: str = Query("beginner", pattern="^(beginner|intermediate|advanced)$"),
    db: Session = Depends(get_db),
):
    """AI-generates short study notes for this topic, scaled to the given difficulty."""
    topic = db.get(models.Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    notes = generate_practice_material(topic.title, topic.summary, difficulty)
    return {"topic_id": topic_id, "difficulty": difficulty, "notes_markdown": notes}
