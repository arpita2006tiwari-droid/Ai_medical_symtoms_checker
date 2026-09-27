import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.medical_report import MedicalReport
from app.schemas import MedicalReportResponse, ReportSummaryResponse
from app.services.auth_service import get_current_user
from app.services.llm_service import llm_service
from app.services.report_service import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])

UPLOAD_DIR = Path("uploads/reports")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE_BYTES = 10 * 1024 * 1024 # 10 MB
ALLOWED_MIMES = ["application/pdf", "image/jpeg", "image/png", "image/webp"]

def validate_report(file: UploadFile):
    if file.content_type not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_MIMES)}")
    
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    return size

@router.post("/", response_model=MedicalReportResponse)
def upload_report(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    size = validate_report(file)
    
    file_id = str(uuid.uuid4())
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
    safe_filename = f"{file_id}.{ext}"
    storage_path = UPLOAD_DIR / safe_filename
    
    try:
        with open(storage_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save report.")
        
    extracted_text = report_service.extract_text(str(storage_path), file.content_type)
    
    status = "extracted"
    if extracted_text.startswith("[Error") or extracted_text.startswith("[Failed"):
        status = "failed"
        
    report_record = MedicalReport(
        id=file_id,
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size,
        storage_path=str(storage_path),
        extracted_text=extracted_text,
        status=status
    )
    
    try:
        db.add(report_record)
        db.commit()
        db.refresh(report_record)
    except Exception as e:
        db.rollback()
        if storage_path.exists():
            try:
                os.remove(storage_path)
            except:
                pass
        raise HTTPException(status_code=500, detail="Failed to save report record to database.")
    
    return report_record

@router.get("/", response_model=list[MedicalReportResponse])
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MedicalReport).filter(MedicalReport.user_id == current_user.id).order_by(MedicalReport.created_at.desc()).all()

@router.get("/{report_id}/content")
def get_report_content(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report_record = db.query(MedicalReport).filter(MedicalReport.id == report_id, MedicalReport.user_id == current_user.id).first()
    if not report_record:
        raise HTTPException(status_code=404, detail="Report not found")
        
    storage_path = Path(report_record.storage_path)
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Report file is missing from storage.")
        
    return FileResponse(storage_path, media_type=report_record.content_type, filename=report_record.filename)

@router.delete("/{report_id}")
def delete_report(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report_record = db.query(MedicalReport).filter(MedicalReport.id == report_id, MedicalReport.user_id == current_user.id).first()
    if not report_record:
        raise HTTPException(status_code=404, detail="Report not found")
        
    storage_path = Path(report_record.storage_path)
    if storage_path.exists():
        try:
            os.remove(storage_path)
        except:
            pass
            
    db.delete(report_record)
    db.commit()
    return {"success": True}

@router.post("/{report_id}/summarize", response_model=ReportSummaryResponse)
def summarize_report(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report_record = db.query(MedicalReport).filter(MedicalReport.id == report_id, MedicalReport.user_id == current_user.id).first()
    if not report_record:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if report_record.content_type == "application/pdf":
        if not report_record.extracted_text or report_record.status == "failed":
            raise HTTPException(status_code=400, detail="Cannot summarize this report. Text extraction failed.")
        summary = llm_service.get_report_summary(report_record.extracted_text, is_image=False)
    else:
        # Image based report
        storage_path = Path(report_record.storage_path)
        if not storage_path.exists():
            raise HTTPException(status_code=404, detail="Report file is missing.")
        try:
            with open(storage_path, "rb") as f:
                image_bytes = f.read()
            summary = llm_service.get_report_summary(image_bytes, is_image=True, mime_type=report_record.content_type)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to read image for summarization.")
            
    return ReportSummaryResponse(summary=summary)
