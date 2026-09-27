import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class ConsultationPreparation(Base):
    __tablename__ = "consultation_preparations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    
    main_concern: Mapped[str] = mapped_column(Text, nullable=False)
    symptoms: Mapped[str] = mapped_column(Text, nullable=True)
    questions: Mapped[str] = mapped_column(Text, nullable=True)
    current_medicines: Mapped[str] = mapped_column(Text, nullable=True)
    allergies: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User")
