from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .core.database import get_db
from .schemas.schemas import UserCreate, UserResponse
from .repositories.user_repository import UserRepository
from .services.ml_client import ml_client

app = FastAPI(title="Ligue 1 Professional API", version="2.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Professional Ligue 1 API"}

@app.post("/users", response_model=UserResponse)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    
    # Vérification si l'email existe
    existing = await repo.get_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await repo.create(user_in)
    return new_user

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict/test")
async def test_prediction(home_team: str, away_team: str):
    # Simulation de features (en prod, elles viendraient de la DB via les stats des équipes)
    dummy_features = {
        "home_elo": 1500.0,
        "away_elo": 1450.0,
        "elo_diff": 50.0,
        "home_form_5": 0.6,
        "away_form_5": 0.4,
        "home_avg_overall": 75.0,
        "away_avg_overall": 72.0,
        "home_squad_value": 200.0,
        "away_squad_value": 150.0,
        "odds_prob_home": 0.45,
        "odds_prob_draw": 0.25,
        "odds_prob_away": 0.30
    }
    
    prediction = await ml_client.get_prediction(dummy_features)
    
    return {
        "match": f"{home_team} vs {away_team}",
        "prediction_result": prediction
    }
