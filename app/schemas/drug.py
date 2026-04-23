from pydantic import BaseModel
# from typing import Optional

class DrugOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True # Allow Pydantic to read data from SQLAlchemy model attributes

class InteractionRequest(BaseModel):
    drug_names: list[str]

class InteractionAlert(BaseModel):
    drug_a: str
    drug_b: str
    description: str

class InteractionResponse(BaseModel):
    checked: list[str]
    interactions_found: int
    alerts: list[InteractionAlert]