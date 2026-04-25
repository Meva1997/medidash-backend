from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class ChecklistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    step: str
    completed: bool
    completed_at: Optional[datetime]
    completed_by: Optional[str] = None
    order_index: int

    @field_validator("completed_by", mode="before")
    @classmethod
    def extract_full_name(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        if hasattr(v, "full_name"):
            return v.full_name  # type: ignore[union-attr]
        return str(v)


class ChecklistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    created_by: int
    created_at: datetime
    notes: Optional[str]
    items: list[ChecklistItemOut]


class ChecklistCreate(BaseModel):
    patient_id: int
    notes: Optional[str] = None


class CompleteItemRequest(BaseModel):
    completed: bool
