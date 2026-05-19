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
PIPELINE_STATUS_PATH = MODELS_DIR / "pipeline_status.json"

def get_model_path(filename: str):
    # Docker path
    docker_path = Path("/app/ml/models") / filename
    if docker_path.exists():
        return docker_path
    
    # Local path (PROJECT_ROOT based)
    local_path = MODELS_DIR / filename
    if local_path.exists():
        return local_path
        
    return Path("ml/models") / filename

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

# --- ROLLING CONFIDENCE CACHE FOR DRIFT DETECTION ---
# Conserve les confiances des 50 dernières requêtes
predictions_confidence_cache = []

def calculate_drift_status() -> int:
    """
    Calcule le statut du Concept Drift en fonction de la dérive de confiance glissante.
    Si la confiance moyenne glissante chute sous 42% sur les 20 derniers matchs, suspecté.
    Si elle chute sous 38%, critique.
    """
    if len(predictions_confidence_cache) < 15:
        return 0 # Pas assez de recul
    
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
        self.metadata_path = MODELS_DIR / "metadata.json"
        
    def get_model(self):
        metadata_file = get_model_path("metadata.json")
        if metadata_file.exists():
            try:
                mtime = os.path.getmtime(metadata_file)
                if mtime > self.last_mtime or self.model is None:
                    print(f"🔄 Détection de changements. Rechargement du modèle dynamique...")
                    with open(metadata_file, "r") as f:
                        meta = json.load(f)
                    
                    chosen_model = meta.get("chosen_production_model", "RandomForestCalibrated")
                    model_info = meta.get("models", {}).get(chosen_model, {})
                    
                    active_file = meta.get("active_model_file", "rf_v1.joblib")
                    model_path = get_model_path(active_file)
                    classes_path = get_model_path("classes.txt")
                    
                    # Chargement en mémoire
                    self.model = joblib.load(str(model_path))
                    with open(classes_path, "r") as f:
                        self.classes = [line.strip() for line in f.readlines()]
                        
                    self.model_name = chosen_model
                    self.model_version = model_info.get("version", "v1")
                    self.calibration_method = meta.get("calibration_method", "sigmoid")
                    self.last_mtime = mtime
                    
                    print(f"✅ Modèle Champion chargé : {self.model_name} ({self.model_version}) avec calibration {self.calibration_method}")
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
            model_path = get_model_path("rf_v1.joblib")
            classes_path = get_model_path("classes.txt")
            if model_path.exists():
                self.model = joblib.load(str(model_path))
                with open(classes_path, "r") as f:
                    self.classes = [line.strip() for line in f.readlines()]
                self.model_name = "RandomForestCalibrated"
                self.model_version = "v1"
                self.calibration_method = "sigmoid"
                print(f"🌲 Modèle standard de secours chargé : {model_path}")
        except Exception as e:
            print(f"❌ Échec du chargement du modèle secours : {e}")

model_manager = DynamicModelManager()

# --- PIPELINE / SCHEDULER MANAGEMENT ---
class PipelineManager:
    @staticmethod
    def get_status():
        if PIPELINE_STATUS_PATH.exists():
            try:
                with open(PIPELINE_STATUS_PATH, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"status": "idle", "timestamp": None, "logs": "Aucune exécution enregistrée."}
        
    @staticmethod
    def write_status(status: str, logs: str):
        try:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            with open(PIPELINE_STATUS_PATH, "w") as f:
                json.dump({
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                    "logs": logs
                }, f, indent=2)
        except Exception as e:
            print(f"Erreur d'écriture statut pipeline : {e}")

def run_pipeline_background_task():
    PipelineManager.write_status("running", "🚀 Démarrage du pipeline de réentraînement continu...\n")
    
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
        
        logs = ""
        for line in process.stdout:
            logs += line
            # Limiter à 150 lignes pour ne pas surcharger la mémoire
            log_lines = logs.split("\n")
            if len(log_lines) > 150:
                logs = "\n".join(log_lines[-150:])
            PipelineManager.write_status("running", logs)
            
        process.wait()
        
        if process.returncode == 0:
            PipelineManager.write_status("success", logs + "\n🎉 Pipeline MLOps exécuté et validé avec succès !")
            PIPELINE_STATUS_GAUGE.set(1)
        else:
            PipelineManager.write_status("failed", logs + f"\n❌ Échec du pipeline. Code de retour : {process.returncode}")
            PIPELINE_STATUS_GAUGE.set(0)
    except Exception as e:
        PipelineManager.write_status("failed", f"❌ Exception fatale pendant l'exécution : {str(e)}")
        PIPELINE_STATUS_GAUGE.set(0)

# --- APIS SCHEDULER JOB ---
scheduler = BackgroundScheduler()

def scheduled_job():
    print("⏰ [Cron Job] Déclenchement automatique hebdomadaire du pipeline ML...")
    run_pipeline_background_task()

@app.on_event("startup")
def startup_event():
    # Déclenchement tous les lundis à 4:00 AM
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
    
    # Charger métadonnées pour statistiques en direct
    active_metrics = {}
    metadata_file = get_model_path("metadata.json")
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
    
    # Mise à jour des métriques Prometheus de production
    PREDICTIONS_COUNTER.labels(outcome=predicted_class, model_version=model_version).inc()
    CONFIDENCE_HISTOGRAM.observe(max_prob)
    
    # Enregistrer la confiance pour le concept drift glissant
    predictions_confidence_cache.append(max_prob)
    if len(predictions_confidence_cache) > 100:
        predictions_confidence_cache.pop(0)
        
    return {
        "prediction": predicted_class,
        "probabilities": result,
        "model": model_name,
        "version": model_version,
        "confidence": max_prob
    }

@app.post("/pipeline/run")
def trigger_pipeline(background_tasks: BackgroundTasks):
    status_info = PipelineManager.get_status()
    if status_info["status"] == "running":
        return {"status": "already_running", "message": "Le pipeline MLOps s'exécute déjà en arrière-plan."}
        
    # Lancement asynchrone
    background_tasks.add_task(run_pipeline_background_task)
    return {"status": "triggered", "message": "Le pipeline MLOps a été lancé en tâche de fond."}

@app.get("/pipeline/status")
def get_pipeline_status():
    return PipelineManager.get_status()

@app.get("/health")
def health():
    model, _, _, _ = model_manager.get_model()
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.get("/metrics")
def get_metrics():
    # Mettre à jour les jauges dynamiques avant l'export
    model, _, model_name, model_version = model_manager.get_model()
    
    metadata_file = get_model_path("metadata.json")
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
            
    # Calcul drift glissant
    DRIFT_GAUGE.set(calculate_drift_status())
    
    return PlainTextResponse(generate_latest(), headers={"Content-Type": CONTENT_TYPE_LATEST})
