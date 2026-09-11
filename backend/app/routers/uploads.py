"""
Learning-material uploads. Files go to Cloudinary; only the resulting
metadata + URL are stored in PostgreSQL for fast retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.cloudinary_service import upload_learning_material, delete_learning_material

router = APIRouter(prefix="/materials", tags=["materials"])


@router.post("/upload", response_model=schemas.LearningMaterialOut, status_code=201)
async def upload_material(
    topic_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    topic = db.get(models.Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    file_bytes = await file.read()
    uploaded = upload_learning_material(file_bytes, filename=file.filename)

    material = models.LearningMaterial(
        topic_id=topic_id,
        title=title,
        resource_type=uploaded["resource_type"],
        cloudinary_public_id=uploaded["public_id"],
        url=uploaded["url"],
        format=uploaded["format"],
        bytes=uploaded["bytes"],
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.delete("/{material_id}", status_code=204)
def delete_material(material_id: int, db: Session = Depends(get_db)):
    material = db.get(models.LearningMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    delete_learning_material(material.cloudinary_public_id, resource_type=material.resource_type)
    db.delete(material)
    db.commit()
    return None
