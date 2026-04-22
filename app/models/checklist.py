from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class SurgicalCheckList(Base):
    __tablename__ = "surgical_checklists"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False) # Foreign key to the patients table so "patients.id" is used to reference the id column in the patients table
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False) # Foreign key to the users table so "users.id" is used to reference the id column in the users table
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True) # Optional notes field for any additional information about the checklist
    patient = relationship("Patient", backref="checklists") # Establishes a relationship between the SurgicalCheckList and Patient models, allowing access to the patient associated with each checklist through the patient attribute
    creator = relationship("User", backref="checklists") # Establishes a relationship between the SurgicalCheckList and User models, allowing access to the creator of each checklist through the creator attribute
    items = relationship("ChecklistItem", back_populates="checklist")

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("surgical_checklists.id"), nullable=False) 
    step = Column(String, nullable=False)
    completed = Column(Boolean, default=False) # Indicates whether the checklist item has been completed or not
    completed_at = Column(DateTime, nullable=True) 
    order_index = Column(Integer, nullable=False) # Used to maintain the order of checklist items within a checklist

    checklist = relationship("SurgicalCheckList", back_populates="items") # Establishes a relationship between the ChecklistItem and SurgicalCheckList models, allowing access to the checklist associated with each item through the checklist attribute