from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.drug import Drug
from app.schemas.drug import DrugOut, InteractionRequest, InteractionResponse, InteractionAlert
from app.core.deps import get_current_user
from app.models.user import User
import json

router = APIRouter(prefix="/drugs", tags=["drugs"])

@router.get("/", response_model=list[DrugOut])
def list_drugs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    drugs = db.query(Drug).all()
    return drugs

@router.post("/interactions", response_model=InteractionResponse)
def check_interacions(payload: InteractionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if len(payload.drug_names) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least two drug names are required to check interactions.")

    #fetch only the requested drugs from the database
    drugs = db.query(Drug).filter(Drug.name.in_(payload.drug_names)).all()

    found_names = {drug.name for drug in drugs}
    not_found = [name for name in payload.drug_names if name not in found_names]

    if not_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Drugs not found: {', '.join(not_found)}")

    #Check every pair once - avoid duplicate checks (A-B and B-A)
    alerts = []
    checked_pairs = set() #to track which pairs have been checked

    for drug in drugs: 
        interactions = json.loads(drug.interactions or "{}")
        for other_name, description in interactions.items():
            if other_name in found_names:
                pair = tuple(sorted([drug.name, other_name]))
                if pair not in checked_pairs:
                    checked_pairs.add(pair)
                    alerts.append(InteractionAlert(
                      drug_a=drug.name,
                      drug_b=other_name,
                      description=description
                    ))
    
    return InteractionResponse(
      checked=payload.drug_names,
      interactions_found=len(alerts),
      alerts=alerts
    )