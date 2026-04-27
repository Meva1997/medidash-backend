from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.patient import Patient
from app.models.consultation import Diagnosis, Prescription
from app.schemas.patient import PatientCreate, PatientOut, NursePatientUpdate
from app.core.deps import get_current_user, require_role, get_patient_or_404
from app.models.user import User, RoleEnum

router = APIRouter(prefix="/patients", tags=["patients"])

#Both roles can view patients
@router.get("/", response_model=list[PatientOut])
def list_patients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Patient).all()

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient: Patient = Depends(get_patient_or_404), current_user: User = Depends(get_current_user)):
    return patient

#Only doctors can create patients
@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(RoleEnum.doctor))):
    patient = Patient(
        **patient_data.model_dump(),
        created_by=current_user.id
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_data: PatientCreate, patient: Patient = Depends(get_patient_or_404), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == RoleEnum.nurse:
        allowed = NursePatientUpdate.model_fields.keys()
        for k, v in patient_data.model_dump().items():
            if k in allowed:
                setattr(patient, k, v)
    else:
        for k, v in patient_data.model_dump().items():
            setattr(patient, k, v)

    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient: Patient = Depends(get_patient_or_404), db: Session = Depends(get_db), current_user: User = Depends(require_role(RoleEnum.doctor))):
    consultation_ids = [c.id for c in patient.consultations]
    if consultation_ids:
        # Self-referential FKs on original_id must be nulled before batch delete
        db.query(Diagnosis).filter(Diagnosis.consultation_id.in_(consultation_ids)).update(
            {"original_id": None}, synchronize_session=False
        )
        db.query(Prescription).filter(Prescription.consultation_id.in_(consultation_ids)).update(
            {"original_id": None}, synchronize_session=False
        )
    db.delete(patient)
    db.commit()
    return None
