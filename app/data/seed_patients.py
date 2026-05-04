from app.database import SessionLocal
from app.models.patient import Patient, GenderEnum
from app.models.user import User
from datetime import datetime, timezone

PATIENTS = [
    {"full_name": "Maria Elena Rodríguez", "age": 34, "gender": GenderEnum.female, "weight_kg": 62.0, "height_cm": 163.0, "glasgow_score": 15},
    {"full_name": "Carlos Mendoza",        "age": 57, "gender": GenderEnum.male,   "weight_kg": 88.5, "height_cm": 175.0, "glasgow_score": 14},
    {"full_name": "Fatima Al-Hassan",      "age": 29, "gender": GenderEnum.female, "weight_kg": 55.0, "height_cm": 158.0, "glasgow_score": 15},
    {"full_name": "David Kim",             "age": 72, "gender": GenderEnum.male,   "weight_kg": 70.0, "height_cm": 168.0, "glasgow_score": 12},
    {"full_name": "Priya Sharma",          "age": 45, "gender": GenderEnum.female, "weight_kg": 68.0, "height_cm": 160.0, "glasgow_score": 15},
    {"full_name": "James Okonkwo",         "age": 38, "gender": GenderEnum.male,   "weight_kg": 95.0, "height_cm": 183.0, "glasgow_score": 15},
    {"full_name": "Ana Luísa Ferreira",    "age": 61, "gender": GenderEnum.female, "weight_kg": 72.5, "height_cm": 162.0, "glasgow_score": 13},
    {"full_name": "Robert Novak",          "age": 53, "gender": GenderEnum.male,   "weight_kg": 82.0, "height_cm": 178.0, "glasgow_score": 14},
    {"full_name": "Yuki Tanaka",           "age": 26, "gender": GenderEnum.female, "weight_kg": 50.0, "height_cm": 155.0, "glasgow_score": 15},
]

def seed():
    db = SessionLocal()
    try:
        creator = db.query(User).first()
        if not creator:
            print("No users found — run auth/register first.")
            return

        added = 0
        for data in PATIENTS:
            exists = db.query(Patient).filter(Patient.full_name == data["full_name"]).first()
            if not exists:
                db.add(Patient(
                    **data,
                    created_by=creator.id,
                    created_at=datetime.now(timezone.utc),
                ))
                added += 1

        db.commit()
        print(f"Seeded {added} patients (skipped {len(PATIENTS) - added} duplicates).")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
