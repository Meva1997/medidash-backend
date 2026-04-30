from pydantic_settings import BaseSettings

# Define the types of the .env variables. In case one is missing the server won't start 
class Settings(BaseSettings):
  DATABASE_URL: str
  SECRET_KEY: str
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 
  ALLOWED_ORIGINS: str = "http://localhost:3000"  # Default value for allowed origins

  class Config:
    env_file = ".env.local", ".env"  # Load .env.local first, then fallback to .env


settings = Settings()  # type: ignore[call-arg]