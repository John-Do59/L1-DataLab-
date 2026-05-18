import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score
)
import xgboost as xgb
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml" / "features" / "ml_dataset.csv"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def train_and_evaluate():
    if not DATASET_PATH.exists():
        print(f"❌ Dataset manquant à l'emplacement : {DATASET_PATH}")
        return

    # 1. Chargement des données
    print("📊 Chargement du dataset L1...")
    df = pd.read_csv(DATASET_PATH)
    
    # Features (12 features compatibles avec app-api et la DB en production)
    features = [
        'home_elo', 'away_elo', 'elo_diff',
        'home_form_5', 'away_form_5',
        'home_avg_overall', 'away_avg_overall',
        'home_squad_value', 'away_squad_value',
        'odds_prob_home', 'odds_prob_draw', 'odds_prob_away'
    ]
    
    # Nettoyage et imputation
    df = df.dropna(subset=['result'])
    df[features] = df[features].fillna(df[features].median())
    
    # Encodage des labels (A, D, H -> 0, 1, 2)
    le = LabelEncoder()
    y = le.fit_transform(df['result'])
    X = df[features]
    
    # 2. Split Temporel (Time-based Split chronologique pour éviter le data leakage)
    print("⏳ Application du Split Temporel (80% Train / 20% Test)...")
    if 'kickoff' in df.columns:
        df['kickoff'] = pd.to_datetime(df['kickoff'])
        df = df.sort_values('kickoff')
        
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"   Train set : {len(X_train)} matchs")
    print(f"   Test set  : {len(X_test)} matchs (les plus récents)")

    # 3. Entraînement Random Forest (Calibré)
    print("🌲 Entraînement du Random Forest Calibré...")
    base_rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=5,
        random_state=42
    )
    # Calibration par validation croisée
    rf_model = CalibratedClassifierCV(estimator=base_rf, method='sigmoid', cv=5)
    rf_model.fit(X_train, y_train)
    
    # 4. Entraînement XGBoost
    print("🚀 Entraînement de XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss'
    )
    xgb_model.fit(X_train, y_train)

    # 5. Évaluation et métriques avancées
    def get_metrics(model, X_t, y_t):
        y_pred = model.predict(X_t)
        y_prob = model.predict_proba(X_t)
        
        auc = roc_auc_score(y_t, y_prob, multi_class='ovr', average='macro')
        
        return {
            "accuracy": float(accuracy_score(y_t, y_pred)),
            "f1_score": float(f1_score(y_t, y_pred, average='macro')),
            "log_loss": float(log_loss(y_t, y_prob)),
            "precision": float(precision_score(y_t, y_pred, average='macro')),
            "recall": float(recall_score(y_t, y_pred, average='macro')),
            "roc_auc": float(auc)
        }

    rf_metrics = get_metrics(rf_model, X_test, y_test)
    xgb_metrics = get_metrics(xgb_model, X_test, y_test)

    print("\n📈 --- RESULTATS (TEST SET) ---")
    print(f"🌲 Random Forest : Accuracy = {rf_metrics['accuracy']:.2%}, Log Loss = {rf_metrics['log_loss']:.4f}")
    print(f"🚀 XGBoost       : Accuracy = {xgb_metrics['accuracy']:.2%}, Log Loss = {xgb_metrics['log_loss']:.4f}")
    
    # 6. Sauvegarde des modèles (joblib) et MLOps Metadata
    print("\n💾 Sauvegarde des artefacts...")
    joblib.dump(rf_model, MODELS_DIR / "rf_v1.joblib")
    joblib.dump(xgb_model, MODELS_DIR / "xgb_v1.joblib")
    joblib.dump(le, MODELS_DIR / "label_encoder_v1.joblib")
    
    # Sauvegarde des classes en texte pour l'API
    with open(MODELS_DIR / "classes.txt", "w") as f:
        for c in le.classes_:
            f.write(f"{c}\n")

    # Metadata MLOps JSON
    metadata = {
        "training_date": datetime.now().isoformat(),
        "dataset_version": "1.0",
        "features_used": features,
        "models": {
            "RandomForestCalibrated": {
                "version": "v1",
                "file": "rf_v1.joblib",
                "hyperparameters": {
                    "n_estimators": 200,
                    "max_depth": 8,
                    "min_samples_split": 5,
                    "calibration": "sigmoid"
                },
                "metrics": rf_metrics
            },
            "XGBoost": {
                "version": "v1",
                "file": "xgb_v1.joblib",
                "hyperparameters": {
                    "n_estimators": 150,
                    "max_depth": 4,
                    "learning_rate": 0.03,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8
                },
                "metrics": xgb_metrics
            }
        },
        "chosen_production_model": "RandomForestCalibrated"
    }
    
    with open(MODELS_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("✅ Modèles et metadata.json sauvegardés avec succès dans ml/models/")

if __name__ == "__main__":
    train_and_evaluate()
