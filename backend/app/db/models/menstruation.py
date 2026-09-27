import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, DateTime, Date, ForeignKey, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class MenstrualCycle(Base):
    __tablename__ = "menstrual_cycles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    cycle_length: Mapped[int] = mapped_column(Integer, nullable=True)
    flow_level: Mapped[str] = mapped_column(String(50), nullable=False)
    cramps_severity: Mapped[int] = mapped_column(Integer, default=0)
    associated_symptoms: Mapped[list] = mapped_column(JSONB, default=list)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="SET NULL"), nullable=True)

class MenstruationPreference(Base):
    __tablename__ = "menstruation_preferences"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_days_before: Mapped[int] = mapped_column(Integer, default=2)
