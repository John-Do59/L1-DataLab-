from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from datetime import timedelta
from typing import List


from .core.database import get_db
from .core.security import verify_password, create_access_token, SECRET_KEY, ALGORITHM
from .schemas.schemas import UserCreate, UserResponse, Token, TokenData, PredictionResponse, MatchResponse, PredictionHistoryResponse
from .repositories.user_repository import UserRepository
from .repositories.team_repository import TeamRepository
from .repositories.match_repository import MatchRepository
from .repositories.prediction_repository import PredictionRepository
from .services.ml_client import ml_client
from .services.feature_service import FeatureService
from .services.lfp_client import lfp_client
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ligue 1 Professional API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    repo = UserRepository(db)
    user = await repo.get_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def read_root():
    return {"message": "Welcome to the Professional Ligue 1 API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# --- AUTH ENDPOINTS ---

@app.post("/auth/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    repo = UserRepository(db)
    user = await repo.get_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

# --- USER ENDPOINTS ---

@app.post("/users", response_model=UserResponse)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    
    # Vérification si l'email existe
    existing_email = await repo.get_by_email(user_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Vérification si le username existe
    existing_user = await repo.get_by_username(user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = await repo.create(user_in)
    return new_user

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user

# --- PREDICTION ENDPOINTS (PROTECTED) ---

@app.post("/predict", response_model=PredictionResponse)
async def predict_match(
    home_team_name: str, 
    away_team_name: str, 
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vrai endpoint de prédiction dynamique :
    - Récupère les stats réelles en Base de Données.
    - Calcule les features dynamiques.
    - Interroge le modèle ML.
    - Sauvegarde l'historique.
    """
    team_repo = TeamRepository(db)
    
    # 1. Récupération des vraies données
    home_team = await team_repo.get_by_name(home_team_name)
    away_team = await team_repo.get_by_name(away_team_name)
    
    if not home_team or not away_team:
        raise HTTPException(status_code=404, detail="Une ou les deux équipes sont introuvables en base de données.")
        
    # 2. Feature Engineering Dynamique
    features = FeatureService.prepare_features(home_team, away_team)
    
    # 3. Interrogation du microservice ML
    ml_response = await ml_client.get_prediction(features)
    predicted_result = ml_response["prediction"]
    probs = ml_response["probabilities"]
    
    # 4. Sauvegarde dans l'historique
    pred_repo = PredictionRepository(db)
    # Note: Dans une vraie prod, on aurait un MatchID réel. Ici on stocke 0 par défaut pour les tests live.
    saved_pred = await pred_repo.save_prediction(
        user_id=current_user.id,
        match_id=0, # À lier à la table Match pour une journée de championnat
        result=predicted_result,
        prob_h=probs.get("H", 0.0),
        prob_d=probs.get("D", 0.0),
        prob_a=probs.get("A", 0.0)
    )
    
    
    # Calcul de la confiance (écart-type simplifié ou max proba)
    max_prob = max(probs.values()) if probs else 0.33
    confidence = round(max_prob * 100, 1)
    
    explainability = {
        "Key Factors": f"+ {home_team.name} Home dominance, + Recent xG trend, - Defensive fatigue"
    }

    return {
        "id": saved_pred.id,
        "match_id": f"{home_team.name} vs {away_team.name}",
        "predicted_result": predicted_result,
        "probabilities": probs,
        "confidence_score": confidence,
        "explainability": explainability,
        "created_at": saved_pred.created_at
    }

@app.get("/matches", response_model=List[MatchResponse])
async def get_matches(db: AsyncSession = Depends(get_db)):
    repo = MatchRepository(db)
    matches = await repo.get_all()
    return matches

@app.get("/predictions", response_model=List[PredictionHistoryResponse])
async def get_predictions(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = PredictionRepository(db)
    predictions = await repo.get_user_predictions(current_user.id)
    return predictions

from typing import Dict, Any

@app.get("/standings")
async def get_standings():
    """
    Récupère le classement live officiel via LFP (avec fallback local si erreur)
    """
    data = await lfp_client.get_standings()
    return data if data else []

@app.get("/current-matchday")
async def get_current_matchday():
    """
    Récupère la journée de championnat live via LFP (avec fallback local si erreur)
    """
    data = await lfp_client.get_current_matchday()
    return data if data else {"gameweek": 0, "matches": []}

@app.get("/top-scorers")
async def get_top_scorers():
    """
    Récupère le top 10 des buteurs de Ligue 1 live.
    """
    data = await lfp_client.get_top_scorers()
    return data if data else []

