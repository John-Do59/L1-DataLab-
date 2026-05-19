import os
import sys
import json
import subprocess
import joblib
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Prometheus & Scheduling
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI(title="Ligue 1 ML API — MLOps Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PATH RESOLUTION ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
CHAMPION_DIR = MODELS_DIR / "champion"
STATE_PATH = MODELS_DIR / "pipeline_state.json"
HISTORY_PATH = MODELS_DIR / "runs_history.json"

def get_champion_paths():
    """
    Retourne les chemins officiels du modèle champion et de son encoder.
    Bascule sur la racine de ml/models en cas d'absence.
    """
    # Chemin conteneurisé Docker
    docker_champion_model = Path("/app/ml/models/champion/champion_model.joblib")
    docker_champion_encoder = Path("/app/ml/models/champion/champion_encoder.joblib")
    if docker_champion_model.exists() and docker_champion_encoder.exists():
        return docker_champion_model, docker_champion_encoder

    # Chemin local
    local_champion_model = CHAMPION_DIR / "champion_model.joblib"
    local_champion_encoder = CHAMPION_DIR / "champion_encoder.joblib"
    if local_champion_model.exists() and local_champion_encoder.exists():
        return local_champion_model, local_champion_encoder

    # Repli racine
    fallback_model = MODELS_DIR / "rf_v1.joblib"
    fallback_encoder = MODELS_DIR / "label_encoder_v1.joblib"
    return fallback_model, fallback_encoder

def get_metadata_path():
    docker_meta = Path("/app/ml/models/metadata.json")
    if docker_meta.exists():
        return docker_meta
    return MODELS_DIR / "metadata.json"

# --- PROMETHEUS METRICS ---
PREDICTIONS_COUNTER = Counter(
    "l1_ml_predictions_total",
    "Nombre de prédictions de matchs effectuées par l'IA",
    ["outcome", "model_version"]
)
CONFIDENCE_HISTOGRAM = Histogram(
    "l1_ml_prediction_confidence",
    "Distribution des probabilités de l'issue prédite gagnante",
    buckets=[0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 1.0]
)
ACCURACY_GAUGE = Gauge(
    "l1_ml_active_model_accuracy",
    "Accuracy du modèle Champion en titre (temporal test set)"
)
BRIER_GAUGE = Gauge(
    "l1_ml_active_model_brier_score",
    "Brier Score du modèle Champion en titre (plus bas est meilleur)"
)
LOGLOSS_GAUGE = Gauge(
    "l1_ml_active_model_log_loss",
    "Log Loss du modèle Champion en titre (plus bas est meilleur)"
)
DRIFT_GAUGE = Gauge(
    "l1_ml_concept_drift_status",
    "Statut de dérive du concept (0 = Stable, 1 = Dérive Suspectée, 2 = Drift Critique)"
)
PIPELINE_STATUS_GAUGE = Gauge(
    "l1_ml_pipeline_last_run_success",
    "Statut du dernier run de pipeline (1 = Succès, 0 = Échec)"
)

# --- ROLLING CONFIDENCE CACHE FOR LIGHTWEIGHT DRIFT INDICATOR ---
predictions_confidence_cache = []

def calculate_drift_status() -> int:
    """
    Calcule le statut du Concept Drift basé sur la confiance glissante moyenne.
    """
    if len(predictions_confidence_cache) < 15:
        return 0
    recent_confidence = predictions_confidence_cache[-20:]
    avg_conf = np.mean(recent_confidence)
    
    if avg_conf < 0.38:
        return 2 # Drift critique
    elif avg_conf < 0.42:
        return 1 # Dérive suspectée
    return 0

# --- DYNAMIC MODEL MANAGER (HOT SERVICE) ---
class DynamicModelManager:
    def __init__(self):
        self.model = None
        self.classes = []
        self.model_name = "RandomForestCalibrated"
        self.model_version = "v1"
        self.calibration_method = "sigmoid"
        self.last_mtime = 0
        
    def get_model(self):
        metadata_file = get_metadata_path()
        if metadata_file.exists():
            try:
                mtime = os.path.getmtime(metadata_file)
                if mtime > self.last_mtime or self.model is None:
                    print(f"🔄 Détection de changements. Rechargement du modèle dynamique...")
                    with open(metadata_file, "r") as f:
                        meta = json.load(f)
                    
                    chosen_model = meta.get("chosen_production_model", "RandomForestCalibrated")
                    model_info = meta.get("models", {}).get(chosen_model, {})
                    
                    active_model_path, active_encoder_path = get_champion_paths()
                    
                    # Chargement sécurisé en mémoire
                    self.model = joblib.load(str(active_model_path))
                    label_encoder = joblib.load(str(active_encoder_path))
                    self.classes = list(label_encoder.classes_)
                        
                    self.model_name = chosen_model
                    self.model_version = model_info.get("version", "v1")
                    self.calibration_method = meta.get("calibration_method", "sigmoid")
                    self.last_mtime = mtime
                    
                    print(f"✅ Modèle Champion rechargé à chaud : {self.model_name} ({self.model_version})")
            except Exception as e:
                print(f"⚠️ Erreur lors du rechargement dynamique : {e}")
                if self.model is None:
                    self.load_static_fallback()
        else:
            if self.model is None:
                self.load_static_fallback()
                
        return self.model, self.classes, self.model_name, self.model_version

    def load_static_fallback(self):
        try:
            active_model_path, active_encoder_path = get_champion_paths()
            if active_model_path.exists() and active_encoder_path.exists():
                self.model = joblib.load(str(active_model_path))
                label_encoder = joblib.load(str(active_encoder_path))
                self.classes = list(label_encoder.classes_)
                self.model_name = "RandomForestCalibrated"
                self.model_version = "v1"
                self.calibration_method = "sigmoid"
                print(f"🌲 Modèle standard de secours chargé : {active_model_path}")
        except Exception as e:
            print(f"❌ Échec du chargement du modèle secours : {e}")

model_manager = DynamicModelManager()

# --- PIPELINE COORDINATOR ---
def run_pipeline_background_task():
    # Résolution de l'exécutable python (local .venv vs global)
    venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
    python_bin = str(venv_python) if venv_python.exists() else sys.executable
    pipeline_script = PROJECT_ROOT / "ml" / "pipeline.py"
    
    try:
        process = subprocess.Popen(
            [python_bin, str(pipeline_script), "--skip-etl"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        
        # Le script pipeline.py gère lui-même le pipeline_state.json de manière robuste,
        # on se contente d'attendre et d'actualiser la jauge Prometheus à la fin.
        process.wait()
        
        if process.returncode == 0:
            PIPELINE_STATUS_GAUGE.set(1)
        else:
            PIPELINE_STATUS_GAUGE.set(0)
    except Exception as e:
        print(f"❌ Exception fatale pendant l'exécution asynchrone : {e}")
        PIPELINE_STATUS_GAUGE.set(0)

# --- APIS SCHEDULER JOB ---
scheduler = BackgroundScheduler()

def scheduled_job():
    print("⏰ [Cron Job] Déclenchement automatique hebdomadaire du pipeline ML...")
    run_pipeline_background_task()

@app.on_event("startup")
def startup_event():
    scheduler.add_job(scheduled_job, "cron", day_of_week="mon", hour=4, minute=0)
    scheduler.start()
    print("⏰ APScheduler démarré (Fréquence : Tous les lundis à 4h00)")
    
    # Premier chargement du modèle
    model_manager.get_model()

# --- PYDANTIC SCHEMAS ---
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

# --- ROUTING ---
@app.get("/")
def read_root():
    model, classes, model_name, model_version = model_manager.get_model()
    
    active_metrics = {}
    metadata_file = get_metadata_path()
    if metadata_file.exists():
        try:
            with open(metadata_file, "r") as f:
                meta = json.load(f)
                active_metrics = meta.get("models", {}).get(model_name, {}).get("metrics", {})
        except Exception:
            pass
            
    return {
        "status": "online",
        "model_loaded": model is not None,
        "model_name": model_name,
        "model_version": model_version,
        "calibration": model_manager.calibration_method,
        "metrics": active_metrics,
        "drift_status": calculate_drift_status()
    }

@app.post("/predict")
def predict(features: MatchFeatures):
    model, classes, model_name, model_version = model_manager.get_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Le modèle n'est pas encore chargé en mémoire.")
    
    # Préparation des features
    input_df = pd.DataFrame([features.dict()])
    
    # Prédiction des probabilités
    probs = model.predict_proba(input_df)[0]
    result = dict(zip(classes, [float(p) for p in probs]))
    
    # Issue prédite et confiance
    predicted_class = classes[probs.argmax()]
    max_prob = float(probs.max())
    
    # Mise à jour des métriques Prometheus
    PREDICTIONS_COUNTER.labels(outcome=predicted_class, model_version=model_version).inc()
    CONFIDENCE_HISTOGRAM.observe(max_prob)
    
    # Enregistrer la confiance pour le concept drift
    predictions_confidence_cache.append(max_prob)
    if len(predictions_confidence_cache) > 100:
        predictions_confidence_cache.pop(0)

    # --- SHAP LOCAL PROXY CALCULATOR (EXPLICABILITÉ) ---
    baselines = {
        "elo_diff": 0.0,
        "home_form_5": 1.3,
        "away_form_5": 1.3,
        "home_squad_value": 120.0,
        "away_squad_value": 120.0,
        "home_avg_overall": 74.0,
        "away_avg_overall": 74.0,
        "odds_prob_home": 0.44,
        "odds_prob_away": 0.32
    }
    stds = {
        "elo_diff": 150.0,
        "home_form_5": 0.5,
        "away_form_5": 0.5,
        "home_squad_value": 80.0,
        "away_squad_value": 80.0,
        "home_avg_overall": 4.0,
        "away_avg_overall": 4.0,
        "odds_prob_home": 0.15,
        "odds_prob_away": 0.12
    }
    global_importances = {
        "elo_diff": 0.285,
        "odds_prob_home": 0.198,
        "home_form_5": 0.124,
        "odds_prob_away": 0.105,
        "away_form_5": 0.092,
        "home_squad_value": 0.081,
        "away_squad_value": 0.065,
        "home_avg_overall": 0.050,
        "away_avg_overall": 0.045
    }
    feature_labels = {
        "elo_diff": "Différence Elo",
        "odds_prob_home": "Cotes Domicile",
        "odds_prob_away": "Cotes Extérieur",
        "home_form_5": "Forme Domicile",
        "away_form_5": "Forme Extérieur",
        "home_squad_value": "Valeur Effectif Dom.",
        "away_squad_value": "Valeur Effectif Ext.",
        "home_avg_overall": "Note FIFA Domicile",
        "away_avg_overall": "Note FIFA Extérieur"
    }

    contributions = []
    for feat_name, baseline in baselines.items():
        feat_val = getattr(features, feat_name, None)
        if feat_val is not None:
            std = stds[feat_name]
            importance = global_importances[feat_name]
            z_score = (feat_val - baseline) / std
            impact = z_score * importance * 15.0
            
            if predicted_class == "H":
                if feat_name in ["elo_diff", "home_form_5", "home_squad_value", "home_avg_overall", "odds_prob_home"]:
                    direction = "positive" if z_score >= 0 else "negative"
                else:
                    direction = "negative" if z_score >= 0 else "positive"
            elif predicted_class == "A":
                if feat_name in ["away_form_5", "away_squad_value", "away_avg_overall", "odds_prob_away"]:
                    direction = "positive" if z_score >= 0 else "negative"
                else:
                    direction = "negative" if z_score >= 0 else "positive"
            else:  # Match Nul "D"
                direction = "positive" if abs(z_score) < 0.8 else "negative"
                impact = (1.0 - min(2.0, abs(z_score))) * importance * 10.0
                
            abs_impact = abs(impact)
            if abs_impact > 0.3:
                contributions.append({
                    "label": feature_labels[feat_name],
                    "impact": round(abs_impact, 1),
                    "direction": direction
                })

    contributions = sorted(contributions, key=lambda x: x["impact"], reverse=True)[:3]
    explainability = {}
    for i, c in enumerate(contributions):
        prefix = "+" if c["direction"] == "positive" else "-"
        explainability[f"Facteur {i+1}"] = f"{prefix} {c['label']} ({prefix}{c['impact']}%)"
        
    return {
        "prediction": predicted_class,
        "probabilities": result,
        "model": model_name,
        "version": model_version,
        "confidence": max_prob,
        "explainability": explainability
    }

@app.post("/pipeline/run")
def trigger_pipeline(background_tasks: BackgroundTasks):
    state_file = STATE_PATH
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
                if state.get("status") == "RUNNING":
                    return {"status": "already_running", "message": "Le pipeline MLOps s'exécute déjà en arrière-plan."}
        except Exception:
            pass
        
    background_tasks.add_task(run_pipeline_background_task)
    return {"status": "triggered", "message": "Le pipeline MLOps a été lancé en tâche de fond."}

@app.get("/pipeline/state")
def get_pipeline_state():
    state_file = STATE_PATH
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_run": None,
        "status": "idle",
        "duration_seconds": 0,
        "current_step": "idle"
    }

@app.get("/pipeline/history")
def get_pipeline_history():
    history_file = HISTORY_PATH
    if history_file.exists():
        try:
            with open(history_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

@app.get("/health")
def health():
    model, _, _, _ = model_manager.get_model()
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.get("/metrics")
def get_metrics():
    model, _, model_name, model_version = model_manager.get_model()
    metadata_file = get_metadata_path()
    if metadata_file.exists():
        try:
            with open(metadata_file, "r") as f:
                meta = json.load(f)
                model_meta = meta.get("models", {}).get(model_name, {})
                metrics = model_meta.get("metrics", {})
                
                ACCURACY_GAUGE.set(metrics.get("accuracy", 0.0))
                BRIER_GAUGE.set(metrics.get("brier_score", 999.0))
                LOGLOSS_GAUGE.set(metrics.get("log_loss", 999.0))
        except Exception:
            pass
            
    DRIFT_GAUGE.set(calculate_drift_status())
    
    state_file = STATE_PATH
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
                status_val = 1 if state.get("status") == "SUCCESS" else 0
                PIPELINE_STATUS_GAUGE.set(status_val)
        except Exception:
            pass
            
    return PlainTextResponse(generate_latest(), headers={"Content-Type": CONTENT_TYPE_LATEST})
