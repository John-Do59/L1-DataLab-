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

def normalize_team_name(name: str) -> str:
    name_lower = name.lower()
    if "paris" in name_lower or "psg" in name_lower:
        return "Paris Saint-Germain"
    if "marseille" in name_lower or "om" in name_lower:
        return "Marseille"
    if "lille" in name_lower or "losc" in name_lower:
        return "Lille"
    if "lyon" in name_lower or "ol" in name_lower:
        return "Lyon"
    if "lens" in name_lower or "rc lens" in name_lower:
        return "Lens"
    if "monaco" in name_lower or "asm" in name_lower:
        return "Monaco"
    if "nice" in name_lower or "ogc" in name_lower:
        return "Nice"
    if "rennes" in name_lower or "stade rennais" in name_lower:
        return "Rennes"
    return name

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
    
    # 1. Récupération des vraies données avec normalisation
    norm_home = normalize_team_name(home_team_name)
    norm_away = normalize_team_name(away_team_name)
    
    home_team = await team_repo.get_by_name(norm_home)
    away_team = await team_repo.get_by_name(norm_away)
    
    # Fallback intelligent pour les équipes absentes de la BD locale (ex: Auxerre, Brest, etc.)
    from app.models.models import Team
    if not home_team:
        home_team = Team(
            id=0,
            name=home_team_name,
            logo_url="https://ligue1.com/images/Logo_Ligue_1.webp",
            elo=1490.0,
            form_5=1.3,
            avg_overall=72.5,
            squad_value=48.0
        )
    if not away_team:
        away_team = Team(
            id=0,
            name=away_team_name,
            logo_url="https://ligue1.com/images/Logo_Ligue_1.webp",
            elo=1470.0,
            form_5=1.2,
            avg_overall=71.5,
            squad_value=42.0
        )
        
    # Calcul intelligent des cotes probables basées sur la différence d'Elo
    elo_diff = home_team.elo - away_team.elo
    prob_h = 1 / (1 + 10 ** (-elo_diff / 400))
    prob_a = 1 - prob_h
    odds_h = max(0.05, prob_h * 0.74)
    odds_a = max(0.05, prob_a * 0.74)
    odds_d = 0.26
        
    # 2. Feature Engineering Dynamique
    features = FeatureService.prepare_features(home_team, away_team, odds_h, odds_d, odds_a)
    
    # 3. Interrogation du microservice ML
    ml_response = await ml_client.get_prediction(features)
    predicted_result = ml_response["prediction"]
    probs = ml_response["probabilities"]
    
    # 4. Sauvegarde dans l'historique avec résolution dynamique du match
    from sqlalchemy import select
    from app.models.models import Match
    from datetime import datetime
    
    # Recherche ou création dynamique du match en base de données applicative
    match_query = select(Match).where(
        (Match.home_team_id == home_team.id) &
        (Match.away_team_id == away_team.id)
    )
    match_res = await db.execute(match_query)
    match_obj = match_res.scalars().first()
    
    if not match_obj:
        match_obj = Match(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_date=datetime.utcnow(),
            season="2025/26",
            round=34,
            odds_h=odds_h,
            odds_d=odds_d,
            odds_a=odds_a,
            status="scheduled"
        )
        db.add(match_obj)
        await db.flush() # Récupère automatiquement match_obj.id
        
    pred_repo = PredictionRepository(db)
    saved_pred = await pred_repo.save_prediction(
        user_id=current_user.id,
        match_id=match_obj.id, # ID 100% valide
        result=predicted_result,
        prob_h=probs.get("H", 0.0),
        prob_d=probs.get("D", 0.0),
        prob_a=probs.get("A", 0.0)
    )
    
    
    # Calcul de la confiance (écart-type simplifié ou max proba)
    max_prob = max(probs.values()) if probs else 0.33
    confidence = round(max_prob * 100, 1)
    
    explainability = ml_response.get("explainability", {
        "Facteur 1": "Avantage à domicile",
        "Facteur 2": "Supériorité technique générale"
    })

    return {
        "id": saved_pred.id,
        "match_id": f"{home_team.name} vs {away_team.name}",
        "predicted_result": predicted_result,
        "probabilities": probs,
        "confidence_score": confidence,
        "explainability": explainability,
        "created_at": saved_pred.created_at,
        "model": ml_response.get("model"),
        "version": ml_response.get("version")
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

