# MediDash API

A RESTful backend for a medical dashboard designed for clinical staff — doctors and nurses — to manage patients, surgical checklists, and drug interaction data.

Built with **FastAPI** and **PostgreSQL**, with a focus on clean architecture, type safety, and production-ready foundations.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Config & Validation | Pydantic v2 / pydantic-settings |
| Runtime | Python 3.11+ |

---

## Features

### Implemented
- **Database schema** — fully migrated via Alembic with versioned history
- **User model** — role-based users (`doctor` / `nurse`) with hashed password storage
- **Patient management** — patient records including biometrics (weight, height) and Glasgow Coma Scale score, linked to the user who created them
- **Drug catalog** — drug records with structured interaction data
- **Surgical checklists** — multi-step checklists tied to a patient and a creator, with per-item completion tracking and ordering
- **Health check endpoint** — `/health` validates live database connectivity
- **CORS** — configured for cross-origin frontend integration
- **JWT authentication** — register and login endpoints (`/auth/register`, `/auth/login`) issuing signed Bearer tokens
- **Role-based access control** — `require_role()` dependency enforces `doctor` / `nurse` permissions per route
- **Password security** — bcrypt hashing via `app/core/security.py`
- **Auth schemas** — `UserCreate`, `UserOut`, and `Token` Pydantic schemas

### In Progress
- **API endpoints** — CRUD routes for patients, drugs, and checklists
- **Request/response schemas** — Pydantic schemas for remaining resources

---

## Project Structure

```
medidash-backend/
├── app/
│   ├── main.py              # FastAPI app, middleware, root routes
│   ├── config.py            # Environment config via pydantic-settings
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models/              # ORM models (User, Patient, Drug, SurgicalChecklist)
│   ├── schemas/
│   │   └── user.py          # UserCreate, UserOut, Token schemas
│   ├── routers/
│   │   └── auth.py          # /auth/register and /auth/login endpoints
│   └── core/
│       ├── security.py      # JWT creation/decoding, bcrypt password utils
│       └── deps.py          # get_current_user, require_role dependencies
├── alembic/                 # Migration scripts
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

API docs available at `http://localhost:8000/docs`

---

## Roadmap

- [x] Project scaffolding and database setup
- [x] Core data models (User, Patient, Drug, Checklist)
- [x] Alembic migration pipeline
- [x] JWT authentication (`/auth/register`, `/auth/login`)
- [x] Role-based access control (RBAC) — doctors vs nurses
- [ ] Full CRUD endpoints for all resources
- [ ] Input validation and error handling
- [ ] Deployment configuration

---

## License

MIT
