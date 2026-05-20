import json
import anthropic
from anthropic.types import TextBlock
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.patient import Patient
from app.schemas.triage import AITriageSuggestRequest, AITriageSuggestResponse, TriageSubmitRequest, TriageSubmitResponse
from app.core.deps import get_current_user
from app.models.user import User
from app.models.triage import TriageRecord
from app.config import settings

router = APIRouter(prefix="/triage", tags=["triage"])

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a clinical decision support assistant specialized in the 
Manchester Triage System (MTS). Given patient data, return ONLY a JSON object — 
no preamble, no markdown, no explanation outside the JSON.

JSON structure:
{
  "recommendedColor": "red" | "orange" | "yellow" | "green" | "blue",
  "confidence": <float 0.0–1.0>,
  "rationale": "<concise clinical rationale in English, max 3 sentences>",
  "suggestedDiscriminators": [
    { "id": "<snake_case_id>", "question": "<yes/no clinical question>", "pointsToColor": "<color>" }
  ]
}

MTS color scale:
- red: immediate vital risk
- orange: very urgent, ≤10 min
- yellow: urgent, ≤60 min
- green: less urgent, ≤120 min
- blue: non-urgent, ≤240 min

Base your recommendation strictly on clinical evidence. 
Suggest 3–5 discriminators relevant to the MTS category provided."""


def build_user_prompt(payload: AITriageSuggestRequest) -> str:
    v = payload.vitals

    # Glasgow total — cast explícito para satisfacer Pylance
    glasgow: int | None = None
    if (
        v.glasgowOcular is not None
        and v.glasgowVerbal is not None
        and v.glasgowMotor is not None
    ):
        glasgow = int(v.glasgowOcular) + int(v.glasgowVerbal) + int(v.glasgowMotor)

    answered = {k: val for k, val in payload.discriminators.items() if val is not None}

    return f"""Patient: {payload.patientAge} years old, sex: {payload.patientSex}
Chief complaint: {payload.complaint}
MTS Category: {payload.mtsCategory}

Vital signs:
- Heart rate: {v.heartRate} bpm
- Respiratory rate: {v.respiratoryRate} rpm
- Blood pressure: {v.systolicBP}/{v.diastolicBP} mmHg
- Temperature: {v.temperature} °C
- SpO2: {v.spO2}%
- Pain scale: {v.painScale}/10
- Capillary glucose: {v.glucoseCapillary if v.glucoseCapillary is not None else 'not measured'} mg/dL
- Glasgow: {glasgow if glasgow is not None else 'not assessed'} (O:{v.glasgowOcular} V:{v.glasgowVerbal} M:{v.glasgowMotor})

Discriminators answered by nurse: {json.dumps(answered) if answered else 'none yet'}"""


@router.post("/ai-suggest", response_model=AITriageSuggestResponse)
async def ai_suggest(
    payload: AITriageSuggestRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_prompt(payload)}],
        )

        # Filtrar explícitamente TextBlock — el SDK puede retornar otros block types
        text_block = next(
            (block for block in message.content if isinstance(block, TextBlock)),
            None,
        )
        if text_block is None:
            raise HTTPException(status_code=502, detail="AI returned no text content")

        raw = text_block.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())

        return AITriageSuggestResponse(**result)

    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI returned invalid JSON")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {str(e)}")

SEX_TO_GENDER = {"M": "male", "F": "female", "O": "other"}


@router.post("", response_model=TriageSubmitResponse, status_code=201)
async def submit_triage(
    payload: TriageSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Calcular edad desde birthDate
    birth = datetime.fromisoformat(payload.patientBirthDate)
    today = datetime.now(timezone.utc)
    age = int((today - birth.replace(tzinfo=timezone.utc)).days / 365.25)

    # Calcular glasgow
    v = payload.vitals
    glasgow = None
    if all(x is not None for x in [v.glasgowOcular, v.glasgowVerbal, v.glasgowMotor]):
        glasgow = int(v.glasgowOcular) + int(v.glasgowVerbal) + int(v.glasgowMotor)  # type: ignore[arg-type]

    # Crear paciente
    patient = Patient(
        full_name=payload.patientName,
        age=age,
        gender=SEX_TO_GENDER[payload.patientSex],
        weight_kg=v.weightKg or 0,
        height_cm=v.heightCm or 0,
        glasgow_score=glasgow,
        created_by=current_user.id,
    )
    db.add(patient)
    db.flush()  # obtener patient.id sin commitear

    # Crear triage record
    record = TriageRecord(
        nurse_id=current_user.id,
        patient_id=patient.id,
        complaint=payload.complaint,
        mts_category=payload.mtsCategory,
        arrival_time=datetime.fromisoformat(payload.arrivalTime),
        vitals=payload.vitals.model_dump(),
        ai_recommended_color=payload.aiRecommendedColor,
        ai_confidence=payload.aiConfidence,
        ai_rationale=payload.aiRationale,
        discriminators=payload.discriminators,
        final_color=payload.finalColor,
        nurse_override=payload.nurseOverride,
        nurse_override_reason=payload.nurseOverrideReason,
        destination=payload.destination,
        census_patient_id=payload.censusPatientId,
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return TriageSubmitResponse(
        triageId=str(record.id),
        createdAt=record.created_at.isoformat(),
        finalColor=str(record.final_color),
        patientName=str(patient.full_name),
    )