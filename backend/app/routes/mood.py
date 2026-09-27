from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.mood import MoodCheckin
from app.schemas import MoodCheckinRequest, MoodCheckinResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/mood", tags=["mood"])

@router.post("/checkins", response_model=MoodCheckinResponse)
def create_mood_checkin(request: MoodCheckinRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkin = MoodCheckin(
        user_id=current_user.id,
        mood=request.mood,
        intensity=request.intensity,
        emotions=request.emotions,
        energy_level=request.energy_level,
        sleep_quality=request.sleep_quality,
        notes=request.notes,
        cycle_id=request.cycle_id
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin

@router.get("/checkins", response_model=list[MoodCheckinResponse])
def get_mood_checkins(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MoodCheckin).filter(MoodCheckin.user_id == current_user.id).order_by(MoodCheckin.created_at.desc()).all()

@router.put("/checkins/{checkin_id}", response_model=MoodCheckinResponse)
def update_mood_checkin(checkin_id: str, request: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkin = db.query(MoodCheckin).filter(MoodCheckin.id == checkin_id, MoodCheckin.user_id == current_user.id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Mood check-in not found")
        
    if "analysis_id" in request:
        checkin.analysis_id = request["analysis_id"]
    if "cycle_id" in request:
        checkin.cycle_id = request["cycle_id"]
        
    db.commit()
    db.refresh(checkin)
    return checkin

@router.delete("/checkins/{checkin_id}")
def delete_mood_checkin(checkin_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkin = db.query(MoodCheckin).filter(MoodCheckin.id == checkin_id, MoodCheckin.user_id == current_user.id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Mood check-in not found")
    db.delete(checkin)
    db.commit()
    return {"success": True}

@router.delete("/checkins")
def delete_all_mood_checkins(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(MoodCheckin).filter(MoodCheckin.user_id == current_user.id).delete()
    db.commit()
    return {"success": True}
