from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from app.database import Base
from datetime import datetime, timezone
from typing import Optional

class SurgicalCheckList(Base):
    __tablename__ = "surgical_checklists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    patient = relationship("Patient", backref=backref("checklists", cascade="all, delete-orphan"))
    creator = relationship("User", backref="checklists")
    items = relationship("ChecklistItem", back_populates="checklist", order_by="ChecklistItem.order_index", cascade="all, delete-orphan")

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    checklist_id: Mapped[int] = mapped_column(ForeignKey("surgical_checklists.id"), nullable=False)
    step: Mapped[str] = mapped_column(nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    order_index: Mapped[int] = mapped_column(nullable=False)

    checklist = relationship("SurgicalCheckList", back_populates="items")
    completed_by = relationship("User")
