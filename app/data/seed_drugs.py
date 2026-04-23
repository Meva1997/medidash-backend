from app.database import SessionLocal
from app.models.drug import Drug
import json # Import json to convert interactions list to JSON string


DRUGS = [
    {"name": "Warfarin", "interactions": {"Aspirin": "High bleeding risk", "Ibuprofen": "Increased anticoagulant effect", "Amoxicillin": "May potentiate anticoagulant effect"}},
    {"name": "Aspirin", "interactions": {"Warfarin": "High bleeding risk", "Ibuprofen": "Increased GI bleeding risk", "Metformin": "May enhance hypoglycemic effect"}},
    {"name": "Metformin", "interactions": {"Aspirin": "May enhance hypoglycemic effect", "Ibuprofen": "Risk of renal impairment reducing metformin clearance"}},
    {"name": "Ibuprofen", "interactions": {"Warfarin": "Increased anticoagulant effect", "Aspirin": "Increased GI bleeding risk", "Metformin": "Risk of renal impairment", "Lisinopril": "Reduced antihypertensive effect"}},
    {"name": "Lisinopril", "interactions": {"Ibuprofen": "Reduced antihypertensive effect", "Potassium": "Risk of hyperkalemia", "Spironolactone": "Risk of hyperkalemia"}},
    {"name": "Amoxicillin", "interactions": {"Warfarin": "May potentiate anticoagulant effect"}},
    {"name": "Spironolactone", "interactions": {"Lisinopril": "Risk of hyperkalemia", "Potassium": "Severe hyperkalemia risk"}},
    {"name": "Potassium", "interactions": {"Lisinopril": "Risk of hyperkalemia", "Spironolactone": "Severe hyperkalemia risk"}},
    {"name": "Digoxin", "interactions": {"Amiodarone": "Increased digoxin toxicity", "Furosemide": "Hypokalemia increases digoxin toxicity"}},
    {"name": "Furosemide", "interactions": {"Digoxin": "Hypokalemia increases digoxin toxicity", "Lithium": "Increased lithium toxicity"}},
    {"name": "Amiodarone", "interactions": {"Digoxin": "Increased digoxin toxicity", "Warfarin": "Significantly increased bleeding risk"}},
    {"name": "Lithium", "interactions": {"Furosemide": "Increased lithium toxicity", "Ibuprofen": "Increased lithium levels"}},
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