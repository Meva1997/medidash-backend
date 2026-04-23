from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

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
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    glasgow_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False) # Foreign key to the users table so "users.id" is used to reference the id column in the users table

    creator = relationship("User", back_populates="patients") # Establishes a relationship between the Patient and User models, allowing access to the creator of each patient record through the creator attribute