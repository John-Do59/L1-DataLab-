from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, List

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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

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
    confidence_score: float = 0.0
    explainability: Dict[str, str] = {}
    created_at: datetime
    model: Optional[str] = None
    version: Optional[str] = None

    class Config:
        from_attributes = True

# --- MATCH & TEAM SCHEMAS ---
class TeamResponse(BaseModel):
    id: int
    name: str
    elo_rating: Optional[float] = None
    logo: Optional[str] = None

    class Config:
        from_attributes = True

class MatchResponse(BaseModel):
    id: int
    home_team: TeamResponse
    away_team: TeamResponse
    match_date: datetime
    status: str

    class Config:
        from_attributes = True

class RagQuestionRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    match_context: Optional[str] = None
    conversation_id: Optional[int] = None

class RagQuestionResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    conversation_id: Optional[int] = None
    mood: Optional[str] = None
    confidence: Optional[float] = None

class PredictionHistoryResponse(BaseModel):
    id: int
    match: MatchResponse
    predicted_result: str
    prob_h: float
    prob_d: float
    prob_a: float
    created_at: datetime
    real_home_score: Optional[int] = None
    real_away_score: Optional[int] = None
    real_status: Optional[str] = None

    class Config:
        from_attributes = True

