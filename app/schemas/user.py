from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import RoleEnum

class UserCreate(BaseModel):
  full_name: str = Field(min_length=2, max_length=100)
  email: EmailStr
  password: str = Field(min_length=8, max_length=50)
  role: RoleEnum

  @field_validator('password')
  @classmethod
  def password_strength(cls, v: str) -> str:
    if len(v) < 8:
      raise ValueError('Password must be at least 8 characters long')
    if len(v) > 50:
      raise ValueError('Password must be at most 50 characters long')
    if not any(char.isupper() for char in v):
      raise ValueError('Password must contain at least one uppercase letter')
    if not any(char.islower() for char in v):
      raise ValueError('Password must contain at least one lowercase letter')
    if not any(char.isdigit() for char in v):
      raise ValueError('Password must contain at least one digit')
    return v

class UserOut(BaseModel):
  id: int
  full_name: str = Field(min_length=2, max_length=100)
  email: EmailStr
  role: RoleEnum

  class Config:
    from_attributes = True

class Token(BaseModel):
  access_token: str
  token_type: str
  id: int
  full_name: str
  email: EmailStr
  role: RoleEnum