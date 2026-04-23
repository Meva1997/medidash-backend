from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.checklist import SurgicalCheckList, ChecklistItem
from app.models.patient import Patient
from app.schemas.checklist import ChecklistCreate, ChecklistOut, CompleteItemRequest
from app.core.deps import get_current_user, require_role
from app.models.user import User, RoleEnum

router = APIRouter(prefix="/checklists", tags=["checklists"])

# Predefined surgical steps — same order every time
SURGICAL_STEPS = [
    "Confirm patient identity and consent",
    "Review allergies and current medications",
    "Verify fasting status (NPO)",
    "Confirm surgical site marking",
    "IV access established",
    "Pre-operative antibiotics administered",
    "Anesthesia team briefed",
    "Equipment and instruments counted",
    "Surgical team timeout completed",
    "Post-op care plan confirmed",
]

@router.post("/", response_model=ChecklistOut, status_code=status.HTTP_201_CREATED)
def create_checklist( data: ChecklistCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(RoleEnum.doctor))): 

    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    checklist = SurgicalCheckList(
      patient_id=data.patient_id,
      created_by=current_user.id,
      notes=data.notes
    )

    db.add(checklist)
    db.flush()  # Get checklist ID before adding items

    for index, step in enumerate(SURGICAL_STEPS):
        item = ChecklistItem(
          checklist_id=checklist.id,
          step=step,
          order_index=index
        )
        db.add(item)
    db.commit()
    db.refresh(checklist)
    return checklist




#Endpint for retrieving a checklist by its ID, including all associated items and their details
@router.get("/{checklist_id}", response_model=ChecklistOut)
def get_checklist(checklist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checklist = db.query(SurgicalCheckList).filter(SurgicalCheckList.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    return checklist




#Endpoint for retrieving all checklists associated with a specific patient, identified by their patient ID. 
@router.get("/patient/{patient_id}", response_model=list[ChecklistOut])
def get_checklists_by_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    checklists = db.query(SurgicalCheckList).filter(SurgicalCheckList.patient_id == patient_id).all()

    if not checklists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No checklists found for this patient")
    
    return checklists




@router.patch("/{checklist_id}/items/{item_id}", response_model=ChecklistOut)
def update_item(
    checklist_id: int,
    item_id: int,
    data: CompleteItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id,
    ChecklistItem.checklist_id == checklist_id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")
    
    item.completed = data.completed 
    item.completed_at = datetime.now(timezone.utc) if data.completed else None

    db.commit()

    checklist = db.query(SurgicalCheckList).filter(SurgicalCheckList.id == checklist_id).first()

    return checklist