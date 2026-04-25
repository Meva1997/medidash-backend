from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.drug import Drug
from app.schemas.drug import DrugOut, InteractionRequest, InteractionResponse, InteractionAlert, SeverityLevel
from app.core.deps import get_current_user
from app.models.user import User
import json
from typing import cast

router = APIRouter(prefix="/drugs", tags=["drugs"])

@router.get("/", response_model=list[DrugOut])
def list_drugs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    drugs = db.query(Drug).all()
    return drugs

@router.post("/interactions", response_model=InteractionResponse)
def check_interacions(payload: InteractionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if len(payload.drug_names) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least two drug names are required to check interactions.")

    drugs = db.query(Drug).filter(Drug.name.in_(payload.drug_names)).all()

    found_names: set[str] = {cast(str, drug.name) for drug in drugs}
    not_found = [name for name in payload.drug_names if name not in found_names]

    if not_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Drugs not found: {', '.join(not_found)}")

    alerts: list[InteractionAlert] = []
    checked_pairs: set[tuple[str, str]] = set()

    for drug in drugs:
        raw: str = cast(str | None, drug.interactions) or "{}"
        interactions: dict[str, dict[str, str] | str] = json.loads(raw)
        for other_name, interaction_data in interactions.items():
            if other_name in found_names:
                pair = (min(cast(str, drug.name), other_name), max(cast(str, drug.name), other_name))
                if pair not in checked_pairs:
                    checked_pairs.add(pair)

                    if isinstance(interaction_data, dict):
                        description: str = interaction_data.get("description", "No description provided.")
                        severity: SeverityLevel = cast(SeverityLevel, interaction_data.get("severity", "Moderate"))
                    else:
                        description = interaction_data
                        severity = "Moderate"

                    alerts.append(InteractionAlert(
                        drug_a=cast(str, drug.name),
                        drug_b=other_name,
                        severity=severity,
                        description=description,
                    ))

    return InteractionResponse(
        checked=payload.drug_names,
        interactions_found=len(alerts),
        alerts=alerts
    )
