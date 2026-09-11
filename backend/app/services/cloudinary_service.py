"""
Cloudinary integration for learning-material uploads. Files are pushed to
Cloudinary; the returned public_id / secure_url / metadata are what get
persisted in PostgreSQL (see models.LearningMaterial) so retrieval afterwards
is just a fast DB read, not another Cloudinary round-trip.
"""
import cloudinary
import cloudinary.uploader

from app.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


def upload_learning_material(file_bytes: bytes, filename: str, folder: str = "learning_materials") -> dict:
    """
    Uploads a file to Cloudinary and returns the fields we persist:
    public_id, secure_url, resource_type, format, bytes.
    `resource_type="auto"` lets Cloudinary detect image / video / raw (pdf, docx, etc).
    """
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="auto",
        use_filename=True,
        unique_filename=True,
        filename=filename,
    )
    return {
        "public_id": result["public_id"],
        "url": result["secure_url"],
        "resource_type": result.get("resource_type", "raw"),
        "format": result.get("format", ""),
        "bytes": result.get("bytes", 0),
    }


def delete_learning_material(public_id: str, resource_type: str = "raw") -> dict:
    return cloudinary.uploader.destroy(public_id, resource_type=resource_type)
