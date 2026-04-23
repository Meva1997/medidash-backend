from pydantic import BaseModel, Field
# from typing import Optional

class DrugOut(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=100)
    class Config:
        from_attributes = True # Allow Pydantic to read data from SQLAlchemy model attributes

class InteractionRequest(BaseModel):
    drug_names: list[str] = Field(min_length=2, max_length=10)

class InteractionAlert(BaseModel):
    drug_a: str = Field(min_length=2, max_length=100)
    drug_b: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=2, max_length=500)

class InteractionResponse(BaseModel):
    checked: list[str]
    interactions_found: int
    alerts: list[InteractionAlert]