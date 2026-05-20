from pydantic import BaseModel
from typing import Optional

class VitalsSchema(BaseModel):
    heartRate: Optional[float] = None
    respiratoryRate: Optional[float] = None
    systolicBP: Optional[float] = None
    diastolicBP: Optional[float] = None
    temperature: Optional[float] = None
    spO2: Optional[float] = None
    glucoseCapillary: Optional[float] = None
    painScale: Optional[float] = None
    weightKg: Optional[float] = None
    heightCm: Optional[float] = None
    glasgowOcular: Optional[int] = None
    glasgowVerbal: Optional[int] = None
    glasgowMotor: Optional[int] = None

class AITriageSuggestRequest(BaseModel):
    complaint: str
    mtsCategory: str
    vitals: VitalsSchema
    discriminators: dict[str, Optional[bool]]
    patientAge: int
    patientSex: str  # "M" | "F" | "O"

class MTSDiscriminator(BaseModel):
    id: str
    question: str
    pointsToColor: str

class AITriageSuggestResponse(BaseModel):
    recommendedColor: str  # "red" | "orange" | "yellow" | "green" | "blue"
    confidence: float       # 0.0 – 1.0
    rationale: str
    suggestedDiscriminators: Optional[list[MTSDiscriminator]] = None

class TriageSubmitRequest(BaseModel):
    patientName: str
    patientBirthDate: str
    patientSex: str
    arrivalTime: str
    complaint: str
    mtsCategory: str
    vitals: VitalsSchema
    discriminators: dict[str, Optional[bool]]
    finalColor: str
    nurseOverride: bool
    nurseOverrideReason: str
    aiRecommendedColor: Optional[str] = None
    aiConfidence: Optional[float] = None
    aiRationale: Optional[str] = None
    destination: str
    censusPatientId: Optional[str] = None
    notes: str

class TriageSubmitResponse(BaseModel):
    triageId: str
    createdAt: str
    finalColor: str
    patientName: str