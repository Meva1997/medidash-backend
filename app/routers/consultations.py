from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.consultation import Consultation, Diagnosis, Prescription, Treatment
from app.models.user import User, RoleEnum
from app.schemas.consultation import (
    ConsultationCreate, ConsultationOut,
    DiagnosisCreate, DiagnosisOut, DiagnosisUpdate,
    TreatmentOut, TreatmentCreate
)
from app.core.deps import get_current_user, require_role,get_patient_or_404, get_consultation_or_404
from app.core.utils import treatments_are_identical

patient_router = APIRouter(tags=["consultations"])
router = APIRouter(prefix="/consultations", tags=["consultations"])


# ── Consultations ────────────────────────────────────────────────────────────

@patient_router.post("/patients/{patient_id}/consultations", response_model=ConsultationOut, status_code=status.HTTP_201_CREATED)
async def create_consultation(
    patient_id: int,
    payload: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.doctor))
):
    get_patient_or_404(patient_id, db)

    consultation = Consultation(
        patient_id=patient_id,
        doctor_id=current_user.id,
        reason=payload.reason,
        notes=payload.notes
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


@patient_router.get("/patients/{patient_id}/consultations", response_model=list[ConsultationOut])
async def list_consultations(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_patient_or_404(patient_id, db)

    return (
        db.query(Consultation)
        .filter(Consultation.patient_id == patient_id)
        .order_by(Consultation.created_at.desc())
        .all()
    )


@router.get("/{consultation_id}", response_model=ConsultationOut)
async def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_consultation_or_404(consultation_id, db)


# ── Diagnoses ────────────────────────────────────────────────────────────────

@router.post(
    "/{consultation_id}/diagnoses",
    response_model=DiagnosisOut,
    status_code=status.HTTP_201_CREATED,
)
def add_diagnosis(
    consultation_id: int,
    payload: DiagnosisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.doctor)),
):
    get_consultation_or_404(consultation_id, db)

    diagnosis = Diagnosis(
        consultation_id=consultation_id,
        description=payload.description,
        diagnosed_by_id=current_user.id,
        diagnosed_by=current_user,
    )
    db.add(diagnosis)
    db.flush()
    diagnosis.original_id = diagnosis.id
    db.commit()
    db.refresh(diagnosis)
    return diagnosis


@router.patch("/{consultation_id}/diagnoses/{diagnosis_id}", response_model=DiagnosisOut)
def update_diagnosis(
    consultation_id: int,
    diagnosis_id: int,
    payload: DiagnosisUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.doctor)),
):
    get_consultation_or_404(consultation_id, db)

    old = db.query(Diagnosis).filter(
        Diagnosis.id == diagnosis_id,
        Diagnosis.consultation_id == consultation_id,
        Diagnosis.is_active,
    ).first()
    if not old:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found.")

    old.is_active = False  # type: ignore[assignment]
    old.superseded_at = datetime.now(timezone.utc)  # type: ignore[assignment]
    old.superseded_by_id = current_user.id  # type: ignore[assignment]

    new = Diagnosis(
        consultation_id=consultation_id,
        description=payload.description,
        diagnosed_by_id=current_user.id,
        original_id=old.original_id,
        diagnosed_by=current_user,
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.get("/{consultation_id}/diagnoses/{diagnosis_id}/history", response_model=list[DiagnosisOut])
def diagnosis_history(
    consultation_id: int,
    diagnosis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_consultation_or_404(consultation_id, db)

    target = db.query(Diagnosis).filter(
        Diagnosis.id == diagnosis_id,
        Diagnosis.consultation_id == consultation_id,
    ).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found.")

    root_id = target.original_id or target.id  # type: ignore[truthy-bool]

    return (
        db.query(Diagnosis)
        .filter(or_(Diagnosis.original_id == root_id, Diagnosis.id == root_id))
        .order_by(Diagnosis.created_at.asc())
        .all()
    )


# ── treatments ────────────────────────────────────────────────────────────

@router.post("/{consultation_id}/treatments", response_model=TreatmentOut, status_code=status.HTTP_201_CREATED)
async def add_treatment(
    consultation_id: int,
    payload: TreatmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.doctor)),
):
    get_consultation_or_404(consultation_id, db)

    active = db.query(Treatment).filter(
        Treatment.consultation_id == consultation_id,
        Treatment.is_active,
    ).first()

    if active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="There is already an active treatment for this consultation. Update the existing one instead.")
    
    treatment = Treatment(
        consultation_id=consultation_id,
        created_by_id=current_user.id,
        created_by=current_user,
    )

    db.add(treatment)
    db.flush()
    treatment.original_id = treatment.id

    for item in payload.prescriptions:
        prescription = Prescription(
            treatment_id=treatment.id,
            prescribed_by_id=current_user.id,
            prescribed_by=current_user,
            medication_name=item.medication_name,
            dose=item.dose,
            frequency=item.frequency,
            duration=item.duration,
            route=item.route,
            instructions=item.instructions,
        )
        db.add(prescription)
    db.commit()
    db.refresh(treatment)
    return treatment


@router.patch("/{consultation_id}/treatments/{treatment_id}", response_model=TreatmentOut)
def update_treatment(
    consultation_id: int,
    treatment_id: int,
    payload: TreatmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.doctor)),
):
    get_consultation_or_404(consultation_id, db)

    old = db.query(Treatment).filter(
        Treatment.id == treatment_id,
        Treatment.consultation_id == consultation_id,
        Treatment.is_active,
    ).first()
    if not old:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found.")
    
    if treatments_are_identical(old.prescriptions, payload.prescriptions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The new treatment is identical to the current active treatment. No changes were made.")

    old.is_active = False  # type: ignore[assignment]
    old.superseded_at = datetime.now(timezone.utc)  # type: ignore[assignment]
    old.superseded_by_id = current_user.id  # type: ignore[assignment]

    # doctor = db.query(User).filter(User.id == current_user.id, User.role == RoleEnum.doctor).first()

    new = Treatment(
        consultation_id=consultation_id,
        created_by_id=current_user.id,
        created_by=current_user,
        original_id=old.original_id,
    )
    db.add(new)
    db.flush()

    for item in payload.prescriptions:
        prescription = Prescription(
            treatment_id=new.id,
            prescribed_by_id=current_user.id,
            prescribed_by=current_user,
            medication_name=item.medication_name,
            dose=item.dose,
            frequency=item.frequency,
            duration=item.duration,
            route=item.route,
            instructions=item.instructions,
        )
        db.add(prescription)
    db.commit()
    db.refresh(new)
    return new


@router.get("/{consultation_id}/treatments", response_model=list[TreatmentOut])
async def list_treatments(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_consultation_or_404(consultation_id, db)

    return (
        db.query(Treatment)
        .filter(
            Treatment.consultation_id == consultation_id,
        )
        .order_by(Treatment.is_active.desc(), Treatment.created_at.desc())
        .all()
    )
