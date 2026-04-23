from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class SurgicalCheckList(Base):
    __tablename__ = "surgical_checklists"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False) 
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False) 
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True) 
    patient = relationship("Patient", backref="checklists") 
    creator = relationship("User", backref="checklists") 
    items = relationship("ChecklistItem", back_populates="checklist")

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("surgical_checklists.id"), nullable=False) 
    step = Column(String, nullable=False)
    completed = Column(Boolean, default=False) 
    completed_at = Column(DateTime, nullable=True) 
    order_index = Column(Integer, nullable=False) 

    checklist = relationship("SurgicalCheckList", back_populates="items") # Establishes a relationship between the ChecklistItem and SurgicalCheckList models, allowing access to the checklist associated with each item through the checklist attribute