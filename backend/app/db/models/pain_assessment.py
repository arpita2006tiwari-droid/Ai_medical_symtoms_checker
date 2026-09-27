import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class PainAssessment(Base):
    __tablename__ = "pain_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    body_region: Mapped[str] = mapped_column(String(100), nullable=False)
    pain_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[int] = mapped_column(Integer, nullable=False)
    onset_duration: Mapped[str] = mapped_column(String(200), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    trend: Mapped[str] = mapped_column(String(100), nullable=False)
    associated_symptoms: Mapped[list] = mapped_column(JSONB, default=list)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="SET NULL"), nullable=True)

    user = relationship("User")
    analysis = relationship("Analysis")
