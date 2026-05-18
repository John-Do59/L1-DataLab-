from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
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

MODEL_PATH = get_model_path("rf_v1.joblib")
CLASSES_PATH = get_model_path("classes.txt")

# Chargement du modèle Random Forest Calibré au démarrage
try:
    if MODEL_PATH.exists():
        model = joblib.load(str(MODEL_PATH))
        with open(CLASSES_PATH, "r") as f:
            classes = [line.strip() for line in f.readlines()]
        print(f"🌲 Modèle Random Forest chargé avec succès depuis {MODEL_PATH}")
    else:
        model = None
        classes = []
        print("⚠️ Fichier de modèle introuvable. L'API ML démarrera sans modèle chargé.")
except Exception as e:
    model = None
    classes = []
    print(f"❌ Erreur lors du chargement du modèle: {str(e)}")

try: 
    # On tente aussi de lire la date et version depuis metadata.json si possible
    metadata_path = get_model_path("metadata.json")
    if metadata_path.exists():
        import json
        with open(metadata_path, 'r') as f:
            meta = json.load(f)
            active_meta = meta["models"]["RandomForestCalibrated"]
            MODEL_NAME = "RandomForestCalibrated"
            MODEL_VERSION = active_meta["version"]
    else:
        MODEL_NAME = "RandomForestCalibrated"
        MODEL_VERSION = "v1"
except Exception:
    MODEL_NAME = "RandomForestCalibrated"
    MODEL_VERSION = "v1"

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
    return {
        "status": "online", 
        "model_loaded": model is not None, 
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION
    }

@app.post("/predict")
def predict(features: MatchFeatures):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Préparation des données pour scikit-learn
    input_df = pd.DataFrame([features.dict()])
    
    # Prédiction des probabilités
    probs = model.predict_proba(input_df)[0]
    
    # Mapping avec les classes (A, D, H)
    result = dict(zip(classes, [float(p) for p in probs]))
    
    # Classe gagnante
    predicted_class = classes[probs.argmax()]
    
    return {
        "prediction": predicted_class,
        "probabilities": result,
        "model": MODEL_NAME,
        "version": MODEL_VERSION
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }
