import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Input
    input_text: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Output arrays stored natively as JSONB
    recognized_symptoms: Mapped[list] = mapped_column(JSONB, default=list)
    unknown_symptoms: Mapped[list] = mapped_column(JSONB, default=list)
    predictions: Mapped[list] = mapped_column(JSONB, default=list)
    symptom_severity: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Objects
    urgency: Mapped[dict] = mapped_column(JSONB, nullable=True)
    specialist_recommendation: Mapped[dict] = mapped_column(JSONB, nullable=True)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    
    analysis_source: Mapped[str] = mapped_column(String(50), nullable=True) # e.g. "predict", "analyze", "chat"

    user = relationship("User", back_populates="analyses")
