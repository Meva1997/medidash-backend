import enum
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class RouteOfAdministration(str, enum.Enum):
    oral = "oral"
    intravenous = "intravenous"
    intramuscular = "intramuscular"
    subcutaneous = "subcutaneous"
    topical = "topical"
    inhalation = "inhalation"
    sublingual = "sublingual"
    rectal = "rectal"
    ophthalmic = "ophthalmic"
    otic = "otic"


class Consultation(Base):
    __tablename__ = 'consultations'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String(500), nullable=False)       
    notes = Column(Text, nullable=True)              
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    patient = relationship("Patient", back_populates="consultations")
    doctor = relationship("User", back_populates="consultations")
    diagnoses = relationship("Diagnosis", back_populates="consultation", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="consultation", cascade="all, delete-orphan")

class Diagnosis(Base):
    __tablename__ = 'diagnoses'

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    diagnosed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Audit trail
    is_active = Column(Boolean, default=True, nullable=False)
    superseded_at = Column(DateTime, nullable=True)
    superseded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=True)

    consultation = relationship("Consultation", back_populates="diagnoses")
    diagnosed_by = relationship("User", foreign_keys="[Diagnosis.diagnosed_by_id]")
    superseded_by = relationship("User", foreign_keys="[Diagnosis.superseded_by_id]")

class Treatment(Base):
    __tablename__ = 'treatments'

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Audit trail — aquí vive ahora, no en cada Prescription
    is_active = Column(Boolean, default=True, nullable=False)
    superseded_at = Column(DateTime, nullable=True)
    superseded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_id = Column(Integer, ForeignKey("treatments.id"), nullable=True)

    consultation = relationship("Consultation", back_populates="treatments")
    created_by = relationship("User", foreign_keys="[Treatment.created_by_id]")
    superseded_by = relationship("User", foreign_keys="[Treatment.superseded_by_id]")
    prescriptions = relationship("Prescription", back_populates="treatment", cascade="all, delete-orphan")


class Prescription(Base):
    __tablename__ = 'prescriptions'

    id = Column(Integer, primary_key=True, index=True)
    treatment_id = Column(Integer, ForeignKey("treatments.id"), nullable=False)

    medication_name = Column(String(255), nullable=False)
    dose = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration = Column(String(100), nullable=False)
    route = Column(Enum(RouteOfAdministration), nullable=False)
    instructions = Column(Text, nullable=True)

    prescribed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    prescribed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    treatment = relationship("Treatment", back_populates="prescriptions")
    prescribed_by = relationship("User", foreign_keys="[Prescription.prescribed_by_id]")
