"""
Course and topic management (the content hierarchy).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=schemas.CourseOut, status_code=201)
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db)):
    course = models.Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=list[schemas.CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()


@router.get("/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.get(models.Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/{course_id}/topics", response_model=schemas.TopicOut, status_code=201)
def add_topic(course_id: int, payload: schemas.TopicCreate, db: Session = Depends(get_db)):
    course = db.get(models.Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    topic = models.Topic(course_id=course_id, **payload.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/{course_id}/topics", response_model=list[schemas.TopicOut])
def list_topics(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Topic).filter(models.Topic.course_id == course_id).order_by(models.Topic.order_index).all()
