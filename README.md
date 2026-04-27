# MediDash API

A RESTful backend for a medical dashboard built for clinical staff — doctors and nurses — to manage patients, surgical checklists, drug safety data, and full consultation records with diagnoses and prescriptions.

Built with **FastAPI** and **PostgreSQL**, with a focus on clean architecture, type safety, role-based security, and production-ready foundations.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy (sync) |
| Migrations | Alembic |
| Config & Validation | Pydantic v2 / pydantic-settings |
| Auth | JWT (python-jose) + bcrypt |
| Runtime | Python 3.11+ |

---

## Features

### Authentication & Security
- **JWT authentication** — register and login endpoints issuing signed Bearer tokens; login response includes the full user profile (`id`, `full_name`, `email`, `role`) alongside the token
- **Role-based access control (RBAC)** — `require_role()` dependency enforces `doctor` / `nurse` permissions per route
- **Password hashing** — bcrypt via `app/core/security.py`
- **Password strength enforcement** — registration rejects passwords missing uppercase, lowercase, or digit characters (enforced via `field_validator` inside `UserCreate`)

### Patient Management
- **Full CRUD** — `GET`, `POST`, `PUT`, `DELETE` under `/patients/`
- **Gender field** — patients carry a `gender` field with enum values `male`, `female`, `other`
- **Role-differentiated updates** — doctors can edit all fields; nurses are restricted to vitals (weight, height, Glasgow score)
- **Computed response fields** — `PatientOut` includes `bmi`, `bmi_category`, and `glasgow_interpretation` derived at response time
- **Safe cascade delete** — deleting a patient nulls self-referential `original_id` FKs on linked diagnoses and prescriptions before cascading, preventing FK constraint violations

### Consultations, Diagnoses & Prescriptions
- **Consultation records** — doctors open a consultation per patient visit, capturing the reason and clinical notes
- **Diagnoses** — doctors add one or more diagnoses per consultation; each supports full-text clinical descriptions
- **Prescriptions** — structured prescription records per consultation including medication name, dose, frequency, duration, and route of administration (oral, IV, IM, subcutaneous, topical, inhalation, sublingual, rectal, ophthalmic, otic)
- **Immutable audit trail** — edits to diagnoses or prescriptions never overwrite records; each update creates a new version and marks the old one inactive (`is_active`, `superseded_at`, `superseded_by_id`, `original_id`), preserving the full clinical history
- **Version history endpoints** — `GET /{consultation_id}/diagnoses/{id}/history` and `GET /{consultation_id}/prescriptions/{id}/history` return the complete revision chain for any record

### Drug Catalog & Interaction Checker
- **Drug listing** — `GET /drugs/` returns the full catalog (authenticated)
- **Interaction checker** — `POST /drugs/interactions` accepts a list of drug names and returns all known pairwise interaction alerts, deduplicating symmetric pairs (A→B and B→A checked once)

### Surgical Checklists
- **Create checklist** — `POST /checklists/` (doctors only) generates a new checklist for a patient pre-populated with 10 standardized surgical safety steps
- **Retrieve by ID** — `GET /checklists/{id}` returns a checklist with all items and completion status
- **Retrieve by patient** — `GET /checklists/patient/{patient_id}` lists all checklists for a given patient; returns an empty list (not 404) when none exist
- **Mark items** — `PATCH /checklists/{checklist_id}/items/{item_id}` toggles item completion, records `completed_at` timestamp, and tracks which user completed each step (`completed_by` returned as the user's full name)

### Data Integrity & Validation
- **Two-layer validation** — every input is validated at the API boundary (Pydantic `Field` constraints and `field_validator`) *and* enforced at the database level (SQLAlchemy `CheckConstraint`)
- **Clinical range enforcement** — age (0–120), weight (0–500 kg), height (0–300 cm), Glasgow Coma Score (3–15) are rejected outside valid ranges by both schema and DB constraint
- **Name sanitization** — patient names are validated against a regex that permits only letters (including Spanish accented characters), spaces, hyphens, and apostrophes
- **Schema-level field bounds** — string fields carry explicit `min_length` / `max_length` limits across all schemas

### Infrastructure
- **Health check** — `GET /health` validates live database connectivity
- **CORS middleware** — configured for cross-origin frontend integration
- **Alembic migrations** — fully versioned schema history

---

## API Overview

| Method | Endpoint | Auth | Role |
|---|---|---|---|
| POST | `/auth/register` | — | — |
| POST | `/auth/login` | — | — |
| GET | `/patients/` | JWT | any |
| GET | `/patients/{id}` | JWT | any |
| POST | `/patients/` | JWT | doctor |
| PUT | `/patients/{id}` | JWT | doctor / nurse* |
| DELETE | `/patients/{id}` | JWT | doctor |
| GET | `/drugs/` | JWT | any |
| POST | `/drugs/interactions` | JWT | any |
| POST | `/checklists/` | JWT | doctor |
| GET | `/checklists/{id}` | JWT | any |
| GET | `/checklists/patient/{patient_id}` | JWT | any |
| PATCH | `/checklists/{id}/items/{item_id}` | JWT | any |
| POST | `/patients/{patient_id}/consultations` | JWT | doctor |
| GET | `/patients/{patient_id}/consultations` | JWT | any |
| GET | `/{consultation_id}` | JWT | any |
| POST | `/{consultation_id}/diagnoses` | JWT | doctor |
| PATCH | `/{consultation_id}/diagnoses/{diagnosis_id}` | JWT | doctor |
| GET | `/{consultation_id}/diagnoses/{diagnosis_id}/history` | JWT | any |
| POST | `/{consultation_id}/prescriptions` | JWT | doctor |
| PATCH | `/{consultation_id}/prescriptions/{prescription_id}` | JWT | doctor |
| GET | `/{consultation_id}/prescriptions/{prescription_id}/history` | JWT | any |
| GET | `/{consultation_id}/prescriptions` | JWT | any |

*Nurses are limited to weight, height, and Glasgow score fields.

---

## Project Structure

```
medidash-backend/
├── app/
│   ├── main.py              # FastAPI app, middleware, router mounts
│   ├── config.py            # Environment config via pydantic-settings
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── user.py          # User model with RoleEnum (doctor / nurse) and DB check constraints
│   │   ├── patient.py       # Patient model with biometrics, GCS score, GenderEnum, and DB check constraints
│   │   ├── drug.py          # Drug model with JSON interaction data
│   │   ├── checklist.py     # SurgicalCheckList and ChecklistItem models
│   │   └── consultation.py  # Consultation, Diagnosis, Prescription models with audit trail
│   ├── schemas/
│   │   ├── user.py          # UserCreate (password strength validation), UserOut, Token (includes user profile fields)
│   │   ├── patient.py       # PatientCreate (name sanitization, range validation), PatientOut, NursePatientUpdate
│   │   ├── drug.py          # DrugOut, InteractionRequest, InteractionResponse
│   │   ├── checklist.py     # ChecklistCreate, ChecklistOut, ChecklistItemOut, CompleteItemRequest
│   │   └── consultation.py  # ConsultationCreate/Out, DiagnosisCreate/Update/Out, PrescriptionCreate/Update/Out
│   ├── routers/
│   │   ├── auth.py          # /auth/register, /auth/login
│   │   ├── patients.py      # Full CRUD for /patients
│   │   ├── drugs.py         # /drugs/ listing and /drugs/interactions
│   │   ├── checklists.py    # Full CRUD for /checklists
│   │   └── consultations.py # Consultations, diagnoses, and prescriptions with audit trail
│   ├── data/
│   │   └── seed_drugs.py    # Drug seeding script
│   └── core/
│       ├── security.py      # JWT creation/decoding, bcrypt utils
│       └── deps.py          # get_current_user, require_role, get_patient_or_404, get_consultation_or_404
├── alembic/                 # Migration scripts (versioned schema history)
└── requirements.txt
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL running locally

### Setup

```bash
# Clone the repo
git clone https://github.com/your-username/medidash-backend.git
cd medidash-backend

# Create and activate virtualenv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file
cp .env.example .env  # then fill in your values
```

### Environment Variables

```env
DATABASE_URL=postgresql://user@localhost:5432/medidash
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Run

```bash
# Apply database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

Interactive API docs available at `http://localhost:8000/docs`

---

## Roadmap

- [x] Project scaffolding and database setup
- [x] Core data models (User, Patient, Drug, Checklist)
- [x] Alembic migration pipeline
- [x] JWT authentication (`/auth/register`, `/auth/login`)
- [x] Role-based access control (RBAC) — doctors vs nurses
- [x] Patient CRUD endpoints with role-differentiated permissions
- [x] Patient response schemas with computed BMI and Glasgow score interpretation
- [x] Drug catalog endpoint and pairwise interaction checker
- [x] Surgical checklist CRUD with standardized safety steps and item completion tracking
- [x] Two-layer input validation — Pydantic field constraints + database-level check constraints
- [x] Gender field on patients (`GenderEnum`: male / female / other)
- [x] Checklist item completion tracking — records which user completed each step
- [x] Consultations system — visit records with reason and clinical notes
- [x] Diagnoses — structured records per consultation (doctor only)
- [x] Prescriptions — structured medication orders with route of administration
- [x] Immutable audit trail — full version history for diagnoses and prescriptions
- [ ] Deployment configuration

---

## License

MIT
