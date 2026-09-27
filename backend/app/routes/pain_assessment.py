from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.pain_assessment import PainAssessment
from app.schemas import PainAssessmentRequest, PainAssessmentResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/pain-assessments", tags=["pain-assessment"])

@router.post("", response_model=PainAssessmentResponse)
def create_pain_assessment(request: PainAssessmentRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_assessment = PainAssessment(
        user_id=current_user.id,
        body_region=request.body_region,
        pain_type=request.pain_type,
        severity=request.severity,
        onset_duration=request.onset_duration,
        frequency=request.frequency,
        trend=request.trend,
        associated_symptoms=request.associated_symptoms,
        notes=request.notes
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@router.put("/{assessment_id}", response_model=PainAssessmentResponse)
def update_pain_assessment(assessment_id: str, request: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_assessment = db.query(PainAssessment).filter(PainAssessment.id == assessment_id, PainAssessment.user_id == current_user.id).first()
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Pain assessment not found")
        
    if "analysis_id" in request:
        db_assessment.analysis_id = request["analysis_id"]
    
    # We can add full editing here later if needed
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@router.get("", response_model=list[PainAssessmentResponse])
def get_pain_assessments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(PainAssessment).filter(PainAssessment.user_id == current_user.id).order_by(PainAssessment.created_at.desc()).all()

@router.delete("/{assessment_id}")
def delete_pain_assessment(assessment_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_assessment = db.query(PainAssessment).filter(PainAssessment.id == assessment_id, PainAssessment.user_id == current_user.id).first()
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Pain assessment not found")
    db.delete(db_assessment)
    db.commit()
    return {"success": True}
