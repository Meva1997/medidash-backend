from pydantic import BaseModel, EmailStr
from app.models.user import RoleEnum

class UserCreate(BaseModel):
  full_name: str
  email: EmailStr
  password: str
  role: RoleEnum

class UserOut(BaseModel):
  id: int
  full_name: str
  email: EmailStr
  role: RoleEnum

  class Config:
    from_attributes = True

class Token(BaseModel):
  access_token: str
  token_type: str

