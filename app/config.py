from pydantic_settings import BaseSettings

# Define the types of the .env variables. In case one is missing the server won't start 
class Settings(BaseSettings):
  DATABASE_URL: str
  SECRET_KEY: str
  ALGORITHM: str
  ACCESS_TOKEN_EXPIRE_MINUTES: int

  class Config:
    env_file = ".env"


settings = Settings()