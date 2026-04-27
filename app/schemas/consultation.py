from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator

from app.models.consultation import RouteOfAdministration


class DiagnosisCreate(BaseModel):
    description: str = Field(..., examples=["Appendicitis"], min_length=3, max_length=2000)


class DiagnosisUpdate(BaseModel):
    description: str = Field(..., examples=["Appendicitis — revised after imaging"], min_length=3, max_length=2000)


class DiagnosisOut(BaseModel):
    id: int
    consultation_id: int
    description: str
    created_at: datetime
    diagnosed_by_id: int
    is_active: bool
    superseded_at: Optional[datetime] = None
    original_id: Optional[int] = None

    model_config = {"from_attributes": True}


class PrescriptionCreate(BaseModel):
    medication_name: str = Field(..., examples=["Acetaminophen"], min_length=3, max_length=255)
    dose: str = Field(..., examples=["500mg"], min_length=2, max_length=100)
    frequency: str = Field(..., examples=["every 8 hours"], min_length=2, max_length=100)
    duration: str = Field(..., examples=["7 days"], min_length=2, max_length=100)
    route: RouteOfAdministration = Field(..., examples=["oral"])
    instructions: Optional[str] = Field(None, examples=["Take with food to avoid stomach upset."], max_length=2000)


class PrescriptionUpdate(BaseModel):
    medication_name: Optional[str] = Field(None, min_length=3, max_length=255)
    dose: Optional[str] = Field(None, min_length=2, max_length=100)
    frequency: Optional[str] = Field(None, min_length=2, max_length=100)
    duration: Optional[str] = Field(None, min_length=2, max_length=100)
    route: Optional[RouteOfAdministration] = None
    instructions: Optional[str] = Field(None, max_length=2000)

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not any([self.medication_name, self.dose, self.frequency, self.duration, self.route, self.instructions]):
            raise ValueError("At least one field must be provided.")
        return self


class PrescriptionOut(BaseModel):
    id: int
    consultation_id: int
    medication_name: str
    dose: str
    frequency: str
    duration: str
    route: RouteOfAdministration
    instructions: Optional[str]
    prescribed_at: datetime
    prescribed_by_id: int
    is_active: bool
    superseded_at: Optional[datetime] = None
    original_id: Optional[int] = None

    model_config = {"from_attributes": True}


class ConsultationCreate(BaseModel):
    reason: str = Field(..., examples=["Patient presents with severe abdominal pain."], min_length=3, max_length=500)
    notes: Optional[str] = Field(None, examples=["The patient has experienced similar episodes in the past."], max_length=2000)


class ConsultationOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    reason: str
    notes: Optional[str]
    created_at: datetime
    diagnoses: list[DiagnosisOut] = []
    prescriptions: list[PrescriptionOut] = []

    @model_validator(mode="after")
    def filter_active(self):
        self.diagnoses = [d for d in self.diagnoses if d.is_active]
        self.prescriptions = [p for p in self.prescriptions if p.is_active]
        return self

    model_config = {"from_attributes": True}
