import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.medical_image import MedicalImage
from app.schemas import MedicalImageResponse, ImageObservationResponse
from app.services.auth_service import get_current_user
from app.services.llm_service import llm_service

router = APIRouter(prefix="/api/images", tags=["images"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE_BYTES = 5 * 1024 * 1024 # 5 MB
ALLOWED_MIMES = ["image/jpeg", "image/png", "image/webp"]

def validate_image(file: UploadFile):
    if file.content_type not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_MIMES)}")
    
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    
    return size

@router.post("/", response_model=MedicalImageResponse)
def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    size = validate_image(file)
    
    file_id = str(uuid.uuid4())
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
    safe_filename = f"{file_id}.{ext}"
    storage_path = UPLOAD_DIR / safe_filename
    
    try:
        with open(storage_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save image.")
        
    image_record = MedicalImage(
        id=file_id,
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size,
        storage_path=str(storage_path)
    )
    
    try:
        db.add(image_record)
        db.commit()
        db.refresh(image_record)
    except Exception as e:
        db.rollback()
        if storage_path.exists():
            try:
                os.remove(storage_path)
            except:
                pass
        raise HTTPException(status_code=500, detail="Failed to save image record to database.")
    
    return image_record

@router.get("/", response_model=list[MedicalImageResponse])
def list_images(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MedicalImage).filter(MedicalImage.user_id == current_user.id).order_by(MedicalImage.created_at.desc()).all()

@router.get("/{image_id}/content")
def get_image_content(image_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    image_record = db.query(MedicalImage).filter(MedicalImage.id == image_id, MedicalImage.user_id == current_user.id).first()
    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
        
    storage_path = Path(image_record.storage_path)
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Image file is missing from storage.")
        
    return FileResponse(storage_path, media_type=image_record.content_type)

@router.delete("/{image_id}")
def delete_image(image_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    image_record = db.query(MedicalImage).filter(MedicalImage.id == image_id, MedicalImage.user_id == current_user.id).first()
    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
        
    storage_path = Path(image_record.storage_path)
    if storage_path.exists():
        try:
            os.remove(storage_path)
        except:
            pass # We still delete DB record if file deletion fails
            
    db.delete(image_record)
    db.commit()
    return {"success": True}

@router.post("/{image_id}/analyze", response_model=ImageObservationResponse)
def analyze_image(image_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    image_record = db.query(MedicalImage).filter(MedicalImage.id == image_id, MedicalImage.user_id == current_user.id).first()
    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
        
    storage_path = Path(image_record.storage_path)
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Image file is missing.")
        
    try:
        with open(storage_path, "rb") as f:
            image_bytes = f.read()
            
        observations = llm_service.get_image_observations(image_bytes, image_record.content_type)
        return ImageObservationResponse(observations=observations)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process image analysis.")
