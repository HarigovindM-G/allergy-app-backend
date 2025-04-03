from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class Medicine(Base):
    """Medicine database model."""
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    dosage = Column(String(255), nullable=False)
    expiration_date = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    reminder_enabled = Column(Boolean, default=False)
    reminder_time = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 