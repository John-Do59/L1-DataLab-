from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import pandas as pd
from pathlib import Path
import os

app = FastAPI(title="Ligue 1 ML API", version="1.0.0")

# Chemins vers le modèle figé (Flexible pour Local vs Docker)
def get_model_path(filename: str):
    # Chemin Docker (racine /app)
    docker_path = Path("/app/ml/models") / filename
    if docker_path.exists():
        return docker_path
    
    # Chemin Local (relatif à main.py)
    local_path = Path(__file__).resolve().parent / "ml" / "models" / filename
    if local_path.exists():
        return local_path
        
    # Fallback racine projet (parents[2] si main.py est dans services/ml-api)
    try:
        fallback_path = Path(__file__).resolve().parents[2] / "ml" / "models" / filename
        if fallback_path.exists():
            return fallback_path
    except IndexError:
        pass
        
    return Path("ml/models") / filename

MODEL_PATH = get_model_path("l1_model_v1.json")
CLASSES_PATH = get_model_path("classes.txt")

# Chargement du modèle au démarrage
model = xgb.XGBClassifier()
if MODEL_PATH.exists():
    model.load_model(str(MODEL_PATH))
    with open(CLASSES_PATH, "r") as f:
        classes = [line.strip() for line in f.readlines()]
else:
    model = None
    classes = []

class MatchFeatures(BaseModel):
    home_elo: float
    away_elo: float
    elo_diff: float
    home_form_5: float
    away_form_5: float
    home_avg_overall: float
    away_avg_overall: float
    home_squad_value: float
    away_squad_value: float
    odds_prob_home: float
    odds_prob_draw: float
    odds_prob_away: float

@app.get("/")
def read_root():
    return {"status": "online", "model_loaded": model is not None}

@app.post("/predict")
def predict(features: MatchFeatures):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Préparation des données pour XGBoost
    input_df = pd.DataFrame([features.dict()])
    
    # Prédiction des probabilités
    probs = model.predict_proba(input_df)[0]
    
    # Mapping avec les classes (A, D, H)
    result = dict(zip(classes, [float(p) for p in probs]))
    
    # Classe gagnante
    predicted_class = classes[probs.argmax()]
    
    return {
        "prediction": predicted_class,
        "probabilities": result
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
