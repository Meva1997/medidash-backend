from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator

from app.models.consultation import RouteOfAdministration


class UserSummary(BaseModel):
    id: int
    full_name: str

    model_config = {"from_attributes": True}


# ── Diagnosis ────────────────────────────────────────────────────────────────

class DiagnosisCreate(BaseModel):
    description: str = Field(..., examples=["Appendicitis"], min_length=3, max_length=2000)


class DiagnosisUpdate(BaseModel):
    description: str = Field(..., examples=["Appendicitis — revised after imaging"], min_length=3, max_length=2000)


class DiagnosisOut(BaseModel):
    id: int
    consultation_id: int
    description: str
    created_at: datetime
    diagnosed_by: UserSummary
    is_active: bool
    superseded_at: Optional[datetime] = None
    superseded_by: Optional[UserSummary] = None
    original_id: Optional[int] = None

    model_config = {"from_attributes": True}


# ── Prescription ─────────────────────────────────────────────────────────────

class PrescriptionCreate(BaseModel):
    medication_name: str = Field(..., examples=["Acetaminophen"], min_length=3, max_length=255)
    dose: str = Field(..., examples=["500mg"], min_length=2, max_length=100)
    frequency: str = Field(..., examples=["every 8 hours"], min_length=2, max_length=100)
    duration: str = Field(..., examples=["7 days"], min_length=2, max_length=100)
    route: RouteOfAdministration = Field(..., examples=["oral"])
    instructions: Optional[str] = Field(None, examples=["Take with food to avoid stomach upset."], max_length=2000)


class PrescriptionOut(BaseModel):
    id: int
    treatment_id: int
    medication_name: str
    dose: str
    frequency: str
    duration: str
    route: RouteOfAdministration
    instructions: Optional[str]
    prescribed_at: datetime
    prescribed_by: UserSummary

    model_config = {"from_attributes": True}


# ── Treatment ─────────────────────────────────────────────────────────────────

class TreatmentCreate(BaseModel):
    prescriptions: list[PrescriptionCreate] = Field(..., min_length=1)


class TreatmentOut(BaseModel):
    id: int
    consultation_id: int
    created_by: UserSummary
    created_at: datetime
    is_active: bool
    superseded_at: Optional[datetime] = None
    superseded_by: Optional[UserSummary] = None
    original_id: Optional[int] = None
    prescriptions: list[PrescriptionOut] = []

    model_config = {"from_attributes": True}


# ── Consultation ──────────────────────────────────────────────────────────────

class ConsultationCreate(BaseModel):
    reason: str = Field(..., examples=["Patient presents with severe abdominal pain."], min_length=3, max_length=500)
    notes: Optional[str] = Field(None, examples=["The patient has experienced similar episodes in the past."], max_length=2000)


class ConsultationOut(BaseModel):
    id: int
    patient_id: int
    doctor: UserSummary
    reason: str
    notes: Optional[str]
    created_at: datetime
    diagnoses: list[DiagnosisOut] = []
    treatments: list[TreatmentOut] = []  # corregido: era list[PrescriptionOut]

    @model_validator(mode="after")
    def filter_active_diagnoses(self):
        self.diagnoses = [d for d in self.diagnoses if d.is_active]
        return self

    model_config = {"from_attributes": True}