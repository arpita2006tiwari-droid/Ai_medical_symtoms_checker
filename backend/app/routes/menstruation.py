from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.menstruation import MenstrualCycle, MenstruationPreference
from app.schemas import MenstrualCycleRequest, MenstrualCycleResponse, MenstruationPreferenceRequest, MenstruationPreferenceResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/menstruation", tags=["menstruation"])

# Preferences
@router.get("/preferences", response_model=MenstruationPreferenceResponse)
def get_preferences(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prefs = db.query(MenstruationPreference).filter(MenstruationPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = MenstruationPreference(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs

@router.put("/preferences", response_model=MenstruationPreferenceResponse)
def update_preferences(request: MenstruationPreferenceRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prefs = db.query(MenstruationPreference).filter(MenstruationPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = MenstruationPreference(user_id=current_user.id)
        db.add(prefs)
    
    prefs.reminders_enabled = request.reminders_enabled
    prefs.reminder_days_before = request.reminder_days_before
    db.commit()
    db.refresh(prefs)
    return prefs

# Cycles
@router.post("/cycles", response_model=MenstrualCycleResponse)
def create_cycle(request: MenstrualCycleRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cycle = MenstrualCycle(
        user_id=current_user.id,
        start_date=request.start_date,
        end_date=request.end_date,
        cycle_length=request.cycle_length,
        flow_level=request.flow_level,
        cramps_severity=request.cramps_severity,
        associated_symptoms=request.associated_symptoms,
        notes=request.notes
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle

@router.get("/cycles", response_model=list[MenstrualCycleResponse])
def get_cycles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MenstrualCycle).filter(MenstrualCycle.user_id == current_user.id).order_by(MenstrualCycle.start_date.desc()).all()

@router.put("/cycles/{cycle_id}", response_model=MenstrualCycleResponse)
def update_cycle(cycle_id: str, request: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cycle = db.query(MenstrualCycle).filter(MenstrualCycle.id == cycle_id, MenstrualCycle.user_id == current_user.id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
        
    if "analysis_id" in request:
        cycle.analysis_id = request["analysis_id"]
    if "end_date" in request:
        from datetime import date
        cycle.end_date = date.fromisoformat(request["end_date"]) if request["end_date"] else None
    
    db.commit()
    db.refresh(cycle)
    return cycle

@router.delete("/cycles/{cycle_id}")
def delete_cycle(cycle_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cycle = db.query(MenstrualCycle).filter(MenstrualCycle.id == cycle_id, MenstrualCycle.user_id == current_user.id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    db.delete(cycle)
    db.commit()
    return {"success": True}

@router.delete("/cycles")
def delete_all_cycles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(MenstrualCycle).filter(MenstrualCycle.user_id == current_user.id).delete()
    db.commit()
    return {"success": True}
