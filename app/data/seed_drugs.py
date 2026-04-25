from app.database import SessionLocal
from app.models.drug import Drug
import json

DRUGS: list[dict[str, str | dict[str, dict[str, str]]]] = [
    {
        "name": "Warfarin",
        "interactions": {
            "Aspirin":      {"description": "High bleeding risk", "severity": "high"},
            "Ibuprofen":    {"description": "Increased anticoagulant effect", "severity": "high"},
            "Amoxicillin":  {"description": "May potentiate anticoagulant effect", "severity": "moderate"},
            "Amiodarone":   {"description": "Significantly increased bleeding risk", "severity": "high"},
        },
    },
    {
        "name": "Aspirin",
        "interactions": {
            "Warfarin":   {"description": "High bleeding risk", "severity": "high"},
            "Ibuprofen":  {"description": "Increased GI bleeding risk", "severity": "high"},
            "Metformin":  {"description": "May enhance hypoglycemic effect", "severity": "moderate"},
        },
    },
    {
        "name": "Metformin",
        "interactions": {
            "Aspirin":    {"description": "May enhance hypoglycemic effect", "severity": "moderate"},
            "Ibuprofen":  {"description": "Risk of renal impairment reducing metformin clearance", "severity": "moderate"},
        },
    },
    {
        "name": "Ibuprofen",
        "interactions": {
            "Warfarin":    {"description": "Increased anticoagulant effect", "severity": "high"},
            "Aspirin":     {"description": "Increased GI bleeding risk", "severity": "high"},
            "Metformin":   {"description": "Risk of renal impairment", "severity": "moderate"},
            "Lisinopril":  {"description": "Reduced antihypertensive effect", "severity": "moderate"},
            "Lithium":     {"description": "Increased lithium levels", "severity": "moderate"},
        },
    },
    {
        "name": "Lisinopril",
        "interactions": {
            "Ibuprofen":      {"description": "Reduced antihypertensive effect", "severity": "moderate"},
            "Potassium":      {"description": "Risk of hyperkalemia", "severity": "high"},
            "Spironolactone": {"description": "Risk of hyperkalemia", "severity": "high"},
        },
    },
    {
        "name": "Amoxicillin",
        "interactions": {
            "Warfarin": {"description": "May potentiate anticoagulant effect", "severity": "moderate"},
        },
    },
    {
        "name": "Spironolactone",
        "interactions": {
            "Lisinopril": {"description": "Risk of hyperkalemia", "severity": "high"},
            "Potassium":  {"description": "Severe hyperkalemia risk", "severity": "high"},
        },
    },
    {
        "name": "Potassium",
        "interactions": {
            "Lisinopril":     {"description": "Risk of hyperkalemia", "severity": "high"},
            "Spironolactone": {"description": "Severe hyperkalemia risk", "severity": "high"},
        },
    },
    {
        "name": "Digoxin",
        "interactions": {
            "Amiodarone":  {"description": "Increased digoxin toxicity", "severity": "high"},
            "Furosemide":  {"description": "Hypokalemia increases digoxin toxicity", "severity": "high"},
        },
    },
    {
        "name": "Furosemide",
        "interactions": {
            "Digoxin":  {"description": "Hypokalemia increases digoxin toxicity", "severity": "high"},
            "Lithium":  {"description": "Increased lithium toxicity", "severity": "high"},
        },
    },
    {
        "name": "Amiodarone",
        "interactions": {
            "Digoxin":   {"description": "Increased digoxin toxicity", "severity": "high"},
            "Warfarin":  {"description": "Significantly increased bleeding risk", "severity": "high"},
        },
    },
    {
        "name": "Lithium",
        "interactions": {
            "Furosemide": {"description": "Increased lithium toxicity", "severity": "high"},
            "Ibuprofen":  {"description": "Increased lithium levels", "severity": "moderate"},
        },
    },
]

def seed():
    db = SessionLocal()
    try:
        for drug_data in DRUGS:
            exists = db.query(Drug).filter(Drug.name == drug_data["name"]).first()
            if not exists:
                drug = Drug(
                    name=drug_data["name"],
                    interactions=json.dumps(drug_data["interactions"]) # Convert interactions dict to JSON string
                )
                db.add(drug)
        db.commit()
        print(f"Seeded {len(DRUGS)} drugs into the database successfully.")
    finally:
        db.close()

# Run the seed function when this script is executed directly, not when imported as a module
if __name__ == "__main__":
    seed()