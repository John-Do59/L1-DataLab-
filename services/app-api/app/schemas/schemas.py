from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- PREDICTION SCHEMAS ---
class PredictionRequest(BaseModel):
    match_id: str
    # Les features brutes si on veut les passer direct, 
    # ou juste l'ID si le backend les calcule
    features: Dict[str, float] 

class PredictionResponse(BaseModel):
    id: int
    match_id: str
    predicted_result: str
    probabilities: Dict[str, float]
    created_at: datetime

    class Config:
        from_attributes = True
