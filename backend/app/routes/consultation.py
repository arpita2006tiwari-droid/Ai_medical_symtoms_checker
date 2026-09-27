from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.consultation import ConsultationPreparation
from app.schemas import ConsultationPreparationRequest, ConsultationPreparationResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/consultations", tags=["consultations"])

@router.post("", response_model=ConsultationPreparationResponse)
def create_consultation_prep(
    request: ConsultationPreparationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prep = ConsultationPreparation(
        user_id=current_user.id,
        main_concern=request.main_concern,
        symptoms=request.symptoms,
        questions=request.questions,
        current_medicines=request.current_medicines,
        allergies=request.allergies
    )
    db.add(db_prep)
    db.commit()
    db.refresh(db_prep)
    return db_prep

@router.get("", response_model=list[ConsultationPreparationResponse])
def get_consultation_preps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ConsultationPreparation)\
        .filter(ConsultationPreparation.user_id == current_user.id)\
        .order_by(ConsultationPreparation.created_at.desc())\
        .all()

@router.get("/{prep_id}", response_model=ConsultationPreparationResponse)
def get_consultation_prep(
    prep_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prep = db.query(ConsultationPreparation)\
        .filter(ConsultationPreparation.id == prep_id, ConsultationPreparation.user_id == current_user.id)\
        .first()
    if not db_prep:
        raise HTTPException(status_code=404, detail="Consultation preparation not found")
    return db_prep

@router.put("/{prep_id}", response_model=ConsultationPreparationResponse)
def update_consultation_prep(
    prep_id: str,
    request: ConsultationPreparationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prep = db.query(ConsultationPreparation)\
        .filter(ConsultationPreparation.id == prep_id, ConsultationPreparation.user_id == current_user.id)\
        .first()
    if not db_prep:
        raise HTTPException(status_code=404, detail="Consultation preparation not found")
        
    db_prep.main_concern = request.main_concern
    db_prep.symptoms = request.symptoms
    db_prep.questions = request.questions
    db_prep.current_medicines = request.current_medicines
    db_prep.allergies = request.allergies
    
    db.commit()
    db.refresh(db_prep)
    return db_prep

@router.delete("/{prep_id}")
def delete_consultation_prep(
    prep_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prep = db.query(ConsultationPreparation)\
        .filter(ConsultationPreparation.id == prep_id, ConsultationPreparation.user_id == current_user.id)\
        .first()
    if not db_prep:
        raise HTTPException(status_code=404, detail="Consultation preparation not found")
        
    db.delete(db_prep)
    db.commit()
    return {"success": True}
