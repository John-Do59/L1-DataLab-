import os
import sys
import json
import pytest
import joblib
from pathlib import Path
from fastapi.testclient import TestClient

# Résoudre le PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "services" / "ml-api"))

from main import app, get_champion_paths, calculate_drift_status, predictions_confidence_cache

client = TestClient(app)

def test_champion_model_paths():
    """
    Vérifie que get_champion_paths retourne bien des chemins existants pour le modèle et l'encodeur.
    """
    model_path, encoder_path = get_champion_paths()
    assert model_path is not None
    assert encoder_path is not None
    assert isinstance(model_path, Path)
    assert isinstance(encoder_path, Path)
    # Soit le champion officiel existe, soit le fallback existe
    assert model_path.exists(), f"Le fichier modèle n'existe pas : {model_path}"
    assert encoder_path.exists(), f"Le fichier encodeur n'existe pas : {encoder_path}"

def test_metadata_integrity():
    """
    Vérifie l'intégrité de la structure du fichier metadata.json s'il existe.
    """
    meta_path = PROJECT_ROOT / "ml" / "models" / "metadata.json"
    if meta_path.exists():
        with open(meta_path, "r") as f:
            meta = json.load(f)
        assert "chosen_production_model" in meta
        assert "models" in meta
        assert "active_version" in meta
        
        chosen_model = meta["chosen_production_model"]
        assert chosen_model in meta["models"]
        assert "metrics" in meta["models"][chosen_model]
        assert "brier_score" in meta["models"][chosen_model]["metrics"]
        assert "accuracy" in meta["models"][chosen_model]["metrics"]

def test_inference_explainability_format():
    """
    Simule une requête de prédiction et valide la structure de retour du modèle,
    notamment la présence et le format des facteurs SHAP proxy d'explicabilité.
    """
    payload = {
        "home_elo": 1650.0,
        "away_elo": 1500.0,
        "elo_diff": 150.0,
        "home_form_5": 2.0,
        "away_form_5": 1.0,
        "home_avg_overall": 78.0,
        "away_avg_overall": 74.0,
        "home_squad_value": 240.0,
        "away_squad_value": 110.0,
        "odds_prob_home": 0.55,
        "odds_prob_draw": 0.25,
        "odds_prob_away": 0.20
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "prediction" in data
    assert data["prediction"] in ["H", "D", "A"]
    assert "probabilities" in data
    assert "H" in data["probabilities"]
    assert "D" in data["probabilities"]
    assert "A" in data["probabilities"]
    assert "model" in data
    assert "version" in data
    assert "confidence" in data
    
    # Validation du SHAP Proxy
    assert "explainability" in data
    assert isinstance(data["explainability"], dict)
    assert len(data["explainability"]) > 0
    
    for key, value in data["explainability"].items():
        assert key.startswith("Facteur")
        # Chaque facteur doit commencer par '+' ou '-'
        assert value.strip().startswith("+") or value.strip().startswith("-")

def test_concept_drift_thresholds():
    """
    Teste la détection glissante du concept drift en manipulant le cache de confiance.
    """
    # Vider temporairement le cache global
    predictions_confidence_cache.clear()
    
    # 1. Cas sous-alimenté (<15 prédictions)
    assert calculate_drift_status() == 0
    
    # 2. Cas stable (Confiance moyenne élevée)
    for _ in range(25):
        predictions_confidence_cache.append(0.55)
    assert calculate_drift_status() == 0
    
    # 3. Cas déviation suspectée (moyenne autour de 0.40)
    predictions_confidence_cache.clear()
    for _ in range(25):
        predictions_confidence_cache.append(0.40)
    assert calculate_drift_status() == 1
    
    # 4. Cas drift critique (moyenne basse autour de 0.35)
    predictions_confidence_cache.clear()
    for _ in range(25):
        predictions_confidence_cache.append(0.35)
    assert calculate_drift_status() == 2
    
    # Restaurer un état propre
    predictions_confidence_cache.clear()
