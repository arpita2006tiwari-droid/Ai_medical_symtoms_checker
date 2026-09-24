from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.analysis import Analysis
from app.schemas import AnalysisResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("", response_model=list[AnalysisResponse])
def get_history(limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id)\
                 .order_by(Analysis.created_at.desc())\
                 .offset(offset).limit(limit).all()
    return analyses

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.delete("/{analysis_id}")
def delete_analysis(analysis_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(analysis)
    db.commit()
    return {"success": True, "message": "Analysis deleted"}
