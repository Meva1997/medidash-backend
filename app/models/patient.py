from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, CheckConstraint, Enum as SAEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
from datetime import datetime, timezone
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (
        CheckConstraint("age >= 0 AND age <= 120", name="valid_age"),
        CheckConstraint("weight_kg > 0 AND weight_kg <= 500", name="valid_weight"),
        CheckConstraint("height_cm > 0 AND height_cm <= 300", name="valid_height"),
        CheckConstraint("glasgow_score >= 3 AND glasgow_score <= 15", name="valid_glasgow_score"),
    )

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(SAEnum(GenderEnum), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    glasgow_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False) # Foreign key to the users table so "users.id" is used to reference the id column in the users table

    creator = relationship("User", back_populates="patients") # Establishes a relationship between the Patient and User models, allowing access to the creator of each patient record through the creator attribute
    consultations = relationship("Consultation", back_populates="patient", cascade="all, delete-orphan") 