import enum
from sqlalchemy import Boolean, Column, Float, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class TriageColor(str, enum.Enum):
    red = "red"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"


class TriageRecord(Base):
    __tablename__ = "triage_records"

    id = Column(Integer, primary_key=True, index=True)
    nurse_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Complaint
    complaint = Column(Text, nullable=False)
    mts_category = Column(String(50), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=False)

    # Vitals snapshot
    vitals = Column(JSON, nullable=False)

    # AI assessment
    ai_recommended_color = Column(Enum(TriageColor), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_rationale = Column(Text, nullable=True)

    # Nurse decision
    discriminators = Column(JSON, nullable=False, default=dict)
    final_color = Column(Enum(TriageColor), nullable=False)
    nurse_override = Column(Boolean, default=False, nullable=False)
    nurse_override_reason = Column(Text, nullable=True)

    # Outcome
    destination = Column(String(50), nullable=False)
    census_patient_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    nurse = relationship("User")
    patient = relationship("Patient")