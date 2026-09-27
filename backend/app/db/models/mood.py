import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class MoodCheckin(Base):
    __tablename__ = "mood_checkins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Core mood fields
    mood: Mapped[str] = mapped_column(String(50), nullable=False) # very low, low, neutral, good, very good
    intensity: Mapped[int] = mapped_column(Integer, nullable=False) # 1-10
    emotions: Mapped[list] = mapped_column(JSONB, default=list) # anxious, sad, stressed, etc.
    
    # Optional fields
    energy_level: Mapped[str] = mapped_column(String(50), nullable=True) # low, medium, high
    sleep_quality: Mapped[str] = mapped_column(String(50), nullable=True) # poor, fair, good, excellent
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Optional associations
    cycle_id: Mapped[str] = mapped_column(String(36), ForeignKey("menstrual_cycles.id", ondelete="SET NULL"), nullable=True)
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="SET NULL"), nullable=True)
