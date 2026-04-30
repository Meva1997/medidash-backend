from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from sqlalchemy import text
from app.routers import auth, patients, drugs, checklists, consultations
from app.config import settings

app = FastAPI(
  title="MediDash API",
  version="1.0.0",
)

origins = settings.ALLOWED_ORIGINS.split(",")

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(drugs.router)
app.include_router(checklists.router)
app.include_router(consultations.router)

@app.get("/")
async def root():
  return {"message": "Welcome to the MediDash API!"}

@app.get("/health")
async def health(): 
  with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
  return {"status": "database connection successful"} 