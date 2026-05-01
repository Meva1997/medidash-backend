# MediDash API

> **Clinical dashboard backend for doctors and nurses** — patient management, surgical checklists, drug interaction checking, and full consultation records with versioned diagnoses and prescriptions.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat)](https://sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-blue?style=flat)](https://alembic.sqlalchemy.org)
[![JWT](https://img.shields.io/badge/Auth-JWT-black?style=flat&logo=jsonwebtokens)](https://jwt.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Live Demo

**Frontend:** [https://medidash-frontend.vercel.app/](https://medidash-frontend.vercel.app/)
**API Docs (Swagger):** available at `/docs` on the deployed backend

---

## What is MediDash?

MediDash is a production-grade REST API designed for clinical teams. It models the real-world workflow of a hospital visit: a doctor opens a consultation, records diagnoses, prescribes treatments, and builds a full immutable audit trail — all while nurses can update patient vitals in parallel. Every business rule (role enforcement, versioned records, no-op guards) is enforced both at the API layer and the database layer.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 (sync) |
| Migrations | Alembic |
| Config & Validation | Pydantic v2 / pydantic-settings |
| Auth | JWT (python-jose) + bcrypt |
| Runtime | Python 3.11+ |

---

## Features

### Authentication & Security
- **JWT authentication** — register and login endpoints issuing signed Bearer tokens; login response includes the full user profile (`id`, `full_name`, `email`, `role`) alongside the token
- **Role-based access control (RBAC)** — `require_role()` dependency enforces `doctor` / `nurse` permissions per route; attempting a restricted action returns 403
- **Password hashing** — bcrypt via `app/core/security.py`
- **Password strength enforcement** — registration rejects passwords missing uppercase, lowercase, or digit characters (enforced via `field_validator` in `UserCreate`)

### Patient Management
- **Full CRUD** — `GET`, `POST`, `PUT`, `DELETE` under `/patients/`
- **Gender field** — patients carry a `gender` field with enum values `male`, `female`, `other`
- **Role-differentiated updates** — doctors can edit all fields; nurses are restricted to vitals (weight, height, Glasgow score)
- **Computed response fields** — `PatientOut` derives `bmi`, `bmi_category`, and `glasgow_interpretation` at response time — no redundant DB columns
- **Safe cascade delete** — deleting a patient nulls self-referential `original_id` FKs on linked diagnoses and treatments before cascading, preventing FK constraint violations

### Consultations, Diagnoses & Treatments
- **Consultation records** — doctors open a consultation per patient visit, capturing the reason and clinical notes
- **Diagnoses** — doctors add one or more diagnoses per consultation; each supports full-text clinical descriptions with an immutable audit trail
- **Treatments** — a treatment groups one or more prescriptions under a single versioned record; posting a new treatment to a consultation automatically supersedes the previous active one
- **Prescriptions** — structured medication orders nested inside a treatment: medication name, dose, frequency, duration, and route of administration (oral, IV, IM, subcutaneous, topical, inhalation, sublingual, rectal, ophthalmic, otic); each prescription carries its own immutable audit trail
- **Immutable audit trail** — edits never overwrite records; each update creates a new version and marks the old one inactive (`is_active`, `superseded_at`, `superseded_by_id`, `original_id`), preserving full clinical history for diagnoses, treatments, and individual prescriptions
- **Version history** — `GET /{consultation_id}/diagnoses/{id}/history` returns the full revision chain for a diagnosis; `GET /{consultation_id}/treatments/{treatment_id}/prescriptions/{prescription_id}/history` returns the revision chain for an individual prescription; all treatment versions returned by `GET /{consultation_id}/treatments`

### Drug Catalog & Interaction Checker
- **Drug listing** — `GET /drugs/` returns the full catalog (authenticated)
- **Pairwise interaction checker** — `POST /drugs/interactions` accepts a list of drug names and returns all known interaction alerts with severity level and description, deduplicating symmetric pairs (A→B and B→A checked once)

### Surgical Checklists
- **Create checklist** — `POST /checklists/` (doctors only) generates a checklist for a patient pre-populated with 10 standardized surgical safety steps
- **Retrieve by ID / by patient** — `GET /checklists/{id}` and `GET /checklists/patient/{patient_id}`
- **Mark items** — `PATCH /checklists/{id}/items/{item_id}` toggles completion, records `completed_at` timestamp, and captures which user completed each step

### Data Integrity & Validation
- **Two-layer validation** — every input validated at the API boundary (Pydantic `Field` constraints + `field_validator`) *and* enforced at the database level (SQLAlchemy `CheckConstraint`)
- **Clinical range enforcement** — age (0–120), weight (0–500 kg), height (0–300 cm), Glasgow Coma Score (3–15) rejected outside valid ranges by both layers
- **Name sanitization** — patient names validated against a regex that permits letters (including Spanish accented characters), spaces, hyphens, and apostrophes
- **Schema-level field bounds** — explicit `min_length` / `max_length` across all schemas

### Infrastructure
- **Health check** — `GET /health` validates live database connectivity
- **CORS middleware** — configured for cross-origin frontend integration
- **Alembic migrations** — fully versioned schema history; safe to run `alembic upgrade head` against any environment

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
| GET | `/consultations/{consultation_id}` | JWT | any |
| POST | `/consultations/{consultation_id}/diagnoses` | JWT | doctor |
| PATCH | `/consultations/{consultation_id}/diagnoses/{diagnosis_id}` | JWT | doctor |
| GET | `/consultations/{consultation_id}/diagnoses/{diagnosis_id}/history` | JWT | any |
| POST | `/consultations/{consultation_id}/treatments` | JWT | doctor |
| PATCH | `/consultations/{consultation_id}/treatments/{treatment_id}/prescriptions/{prescription_id}` | JWT | doctor |
| GET | `/consultations/{consultation_id}/treatments/{treatment_id}/prescriptions/{prescription_id}/history` | JWT | any |
| GET | `/consultations/{consultation_id}/treatments` | JWT | any |

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
│   │   └── consultation.py  # Consultation, Diagnosis, Treatment, Prescription models with audit trail
│   ├── schemas/
│   │   ├── user.py          # UserCreate (password strength validation), UserOut, Token
│   │   ├── patient.py       # PatientCreate (name sanitization, range validation), PatientOut, NursePatientUpdate
│   │   ├── drug.py          # DrugOut, InteractionRequest, InteractionAlert (with SeverityLevel), InteractionResponse
│   │   ├── checklist.py     # ChecklistCreate, ChecklistOut, ChecklistItemOut, CompleteItemRequest
│   │   └── consultation.py  # ConsultationCreate/Out, DiagnosisCreate/Update/Out, TreatmentCreate/Out, PrescriptionCreate/Update/Out
│   ├── routers/
│   │   ├── auth.py          # /auth/register, /auth/login
│   │   ├── patients.py      # Full CRUD for /patients
│   │   ├── drugs.py         # /drugs/ listing and /drugs/interactions
│   │   ├── checklists.py    # Full CRUD for /checklists
│   │   └── consultations.py # Consultations, diagnoses, and treatments with audit trail
│   ├── data/
│   │   └── seed_drugs.py    # Drug seeding script
│   └── core/
│       ├── security.py      # JWT creation/decoding, bcrypt utils
│       ├── deps.py          # get_current_user, require_role, get_patient_or_404, get_consultation_or_404
│       └── utils.py         # shared utilities
├── alembic/                 # Migration scripts (fully versioned schema history)
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
git clone https://github.com/Meva1997/medidash-backend.git
cd medidash-backend

# Create and activate virtualenv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file with the required variables (see below)
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

# Seed the drug catalog
python -m app.data.seed_drugs

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
- [x] Treatments — grouped prescription orders per consultation with immutable versioning
- [x] Prescriptions — structured medication orders nested inside a treatment, with route of administration
- [x] Immutable audit trail — full version history for diagnoses, treatments, and individual prescriptions
- [x] Per-prescription versioning — prescriptions updated individually with their own audit trail and history endpoint
- [x] Deployment — live at [medidash-frontend.vercel.app](https://medidash-frontend.vercel.app/)

---

## License

MIT
