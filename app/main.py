from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from sqlalchemy import text
from app.routers import auth

app = FastAPI(
  title="MediDash API",
  version="1.0.0",
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"], #!In production, specify the allowed origins instead of using "*"
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
async def root():
  return {"message": "Welcome to the MediDash API!"}

@app.get("/health")
async def health(): 
  with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
  return {"status": "database connection successful"} 