# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Dev Setup

Requires a `.env` file at the project root with:
```
DATABASE_URL=postgresql://alexmedina@localhost:5432/medidash
SECRET_KEY=<secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Activate the virtualenv before running anything:
```bash
source venv/bin/activate
```

## Commands

```bash
# Start the dev server
uvicorn app.main:app --reload

# Generate a new migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Architecture

**Stack:** FastAPI · SQLAlchemy (sync) · PostgreSQL · Alembic · pydantic-settings

**Request flow:** `app/main.py` mounts routers → routers use `get_db()` dependency from `app/database.py` → routers call into models/schemas.

**Config** (`app/config.py`): Pydantic `BaseSettings` loads from `.env`. All settings are accessed via the `settings` singleton. The server won't start if any required env var is missing.

**Models** (`app/models/`): SQLAlchemy ORM classes that map to the DB. All inherit from `Base` (defined in `app/database.py`). Current domain:
- `User` — doctors and nurses (`RoleEnum`)
- `Patient` — linked to creating `User` via `created_by` FK; includes `gender` (`GenderEnum`: male/female/other) and Glasgow Coma Scale score
- `Drug` — stores drug interactions as a JSON string in a `Text` column
- `SurgicalCheckList` / `ChecklistItem` — checklists tied to a patient and creator; items have `order_index` for ordering, `completed`/`completed_at` for status, and `completed_by_id` (FK to `users`) to track who completed each step

**Schemas** (`app/schemas/`):
- `user.py` — `UserCreate`, `UserOut`, `Token`
- `patient.py` — `PatientCreate`, `PatientOut` (includes `gender`, computed fields: `bmi`, `bmi_category`, `glasgow_interpretation`), `NursePatientUpdate` (vitals-only subset for nurse updates; gender is not editable by nurses)
- `drug.py` — `DrugOut`, `InteractionRequest`, `InteractionAlert`, `InteractionResponse`
- `checklist.py` — `ChecklistCreate`, `ChecklistOut`, `ChecklistItemOut` (includes `completed_by` as the full name of the completing user), `CompleteItemRequest`

**Routers** (`app/routers/`):
- `auth.py` — `/auth/register`, `/auth/login`
- `patients.py` — full CRUD under `/patients`; doctors can create/delete/update all fields; nurses can only update vitals (weight, height, Glasgow score)
- `drugs.py` — `GET /drugs/` lists all drugs; `POST /drugs/interactions` checks pairwise interactions from a list of drug names (deduplicates symmetric pairs)
- `checklists.py` — `POST /checklists/` (doctor only) creates a checklist pre-filled with 10 standardized surgical steps; `GET /checklists/{id}`; `GET /checklists/patient/{patient_id}`; `PATCH /checklists/{id}/items/{item_id}` to toggle completion and record who completed it

**Data** (`app/data/`):
- `seed_drugs.py` — script to seed the drug catalog into the database

**Dependencies** (`app/core/deps.py`):
- `get_current_user` — decodes JWT and returns the authenticated `User`
- `require_role(*roles)` — raises 403 if the current user's role is not in the allowed list
- `get_patient_or_404` — fetches `Patient` by path param `patient_id` or raises 404

**Migrations** (`alembic/`): `alembic/env.py` imports `app.models` (the package `__init__.py`) to register all models with SQLAlchemy metadata before autogenerate runs. When adding a new model, import it in `app/models/__init__.py`.
