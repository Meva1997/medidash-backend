from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChecklistItemOut(BaseModel):
    id: int
    step: str
    completed: bool
    completed_at: Optional[datetime]
    order_index: int

    class Config:
        from_attributes = True

class ChecklistOut(BaseModel):
    id: int
    patient_id: int
    created_by: int
    created_at: datetime
    notes: Optional[str]
    items: list[ChecklistItemOut]

    class Config:
        from_attributes = True

class ChecklistCreate(BaseModel):
    patient_id: int
    notes: Optional[str] = None

class CompleteItemRequest(BaseModel):
    completed: bool