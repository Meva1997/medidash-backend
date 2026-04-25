import re
from pydantic import BaseModel, computed_field, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.patient import GenderEnum

class PatientCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=120)
    gender: GenderEnum
    weight_kg: float = Field(ge=0, le=500)
    height_cm: float = Field(ge=0, le=300)
    glasgow_score: Optional[int] = Field(None, ge=3, le=15)

    @field_validator("full_name")
    @classmethod
    def sanitize_name(cls, v):
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s\-']+$", v):
            raise ValueError("Name contains invalid characters")
        return v.strip()



class PatientOut(BaseModel):
    id: int
    full_name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=120)
    gender: GenderEnum
    weight_kg: float = Field(ge=0, le=500)
    height_cm: float = Field(ge=0, le=300)
    glasgow_score: Optional[int] = Field(None, ge=3, le=15)
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True # Allow creating PatientOut from ORM objects
    
    # This is a computed field that calculates BMI based on weight and height
    @computed_field
    @property
    def bmi(self) -> float:
        if self.height_cm == 0:
            return 0.0
        return self.weight_kg / ((self.height_cm / 100) ** 2)

    @computed_field
    @property
    def bmi_category(self) -> str:
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "Underweight"
        elif 18.5 <= bmi_value <= 24.9:
            return "Normal weight"
        elif 25 <= bmi_value <= 29.9:
            return "Overweight"
        elif 30 <= bmi_value <= 34.9:
            return "Obesity I"
        elif 35 <= bmi_value <= 39.9:
            return "Obesity II"
        else:
            return "Obesity III"
    
    @computed_field
    @property
    def glasgow_interpretation(self) -> Optional[str]:
        if self.glasgow_score is None:
            return None
        if self.glasgow_score <= 8:
            return "Severe brain injury"
        elif self.glasgow_score <= 12:
            return "Moderate brain injury"
        else:
            return "Mild / Normal brain injury"

class NursePatientUpdate(BaseModel):
    weight_kg: float
    height_cm: float
    glasgow_score: Optional[int] = None

