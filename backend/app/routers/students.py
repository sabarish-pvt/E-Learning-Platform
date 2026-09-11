"""
Student management: registration, login, profile retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Student).filter(models.Student.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    student = models.Student(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    token = create_access_token(subject=str(student.id))
    return {"access_token": token, "student": student}


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.StudentLogin, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.email == payload.email).first()
    if not student or not verify_password(payload.password, student.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=str(student.id))
    return {"access_token": token, "student": student}


@router.get("", response_model=list[schemas.StudentOut])
def list_students(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.Student).offset(skip).limit(limit).all()


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
