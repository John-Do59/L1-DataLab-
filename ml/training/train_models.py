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
from sklearn.calibration import calibration_curve
import xgboost as xgb
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml" / "features" / "ml_dataset.csv"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def compute_multiclass_brier_score(y_true, y_prob):
    """
    Calcule le Brier Score multi-classe (erreur quadratique moyenne des probabilités).
    BS = 1/N * sum_{i=1}^N sum_{j=1}^C (p_ij - y_ij)^2
    """
    N, C = y_prob.shape
    y_true_one_hot = np.zeros((N, C))
    y_true_one_hot[np.arange(N), y_true] = 1.0
    # Somme des carrés des différences par ligne, puis moyenne sur toutes les lignes
    return float(np.mean(np.sum((y_prob - y_true_one_hot) ** 2, axis=1)))

def compute_calibration_curve_h(y_true, y_prob):
    """
    Calcule les points de la courbe de calibration pour l'issue 'H' (Victoire Domicile, index 2).
    """
    y_true_h = (y_true == 2).astype(int)
    prob_h = y_prob[:, 2]
    # Calcul des bins uniformes pour la courbe de fiabilité
    prob_true, prob_pred = calibration_curve(y_true_h, prob_h, n_bins=5, strategy='uniform')
    return prob_true.tolist(), prob_pred.tolist()

def train_and_evaluate(calibration_method='sigmoid'):
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"❌ Dataset manquant à l'emplacement : {DATASET_PATH}")

    # 1. Chargement des données
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
    
    # 2. Split Temporel chronologique (80% Train / 20% Test)
    if 'kickoff' in df.columns:
        df['kickoff'] = pd.to_datetime(df['kickoff'])
        df = df.sort_values('kickoff')
        
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # 3. Entraînement Random Forest (Calibré selon méthode passée en paramètre)
    base_rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=5,
        random_state=42
    )
    if calibration_method in ['sigmoid', 'isotonic']:
        rf_model = CalibratedClassifierCV(estimator=base_rf, method=calibration_method, cv=5)
    else:
        rf_model = base_rf
        
    rf_model.fit(X_train, y_train)
    
    # 4. Entraînement XGBoost
    xgb_model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss'
    )
    # XGBoost peut également bénéficier d'une calibration
    if calibration_method in ['sigmoid', 'isotonic']:
        xgb_calibrated = CalibratedClassifierCV(estimator=xgb_model, method=calibration_method, cv=5)
        xgb_calibrated.fit(X_train, y_train)
        active_xgb = xgb_calibrated
    else:
        xgb_model.fit(X_train, y_train)
        active_xgb = xgb_model

    # 5. Évaluation et métriques avancées
    def get_metrics(model, X_t, y_t):
        y_pred = model.predict(X_t)
        y_prob = model.predict_proba(X_t)
        
        auc = roc_auc_score(y_t, y_prob, multi_class='ovr', average='macro')
        brier = compute_multiclass_brier_score(y_t, y_prob)
        cal_true, cal_pred = compute_calibration_curve_h(y_t, y_prob)
        
        return {
            "accuracy": float(accuracy_score(y_t, y_pred)),
            "f1_score": float(f1_score(y_t, y_pred, average='macro')),
            "log_loss": float(log_loss(y_t, y_prob)),
            "brier_score": brier,
            "precision": float(precision_score(y_t, y_pred, average='macro')),
            "recall": float(recall_score(y_t, y_pred, average='macro')),
            "roc_auc": float(auc),
            "calibration_curve_h": {
                "prob_true": cal_true,
                "prob_pred": cal_pred
            }
        }

    rf_metrics = get_metrics(rf_model, X_test, y_test)
    xgb_metrics = get_metrics(active_xgb, X_test, y_test)

    return {
        "rf_model": rf_model,
        "xgb_model": active_xgb,
        "label_encoder": le,
        "rf_metrics": rf_metrics,
        "xgb_metrics": xgb_metrics,
        "features_used": features,
        "metadata": {
            "training_date": datetime.now().isoformat(),
            "dataset_version": "2.0",
            "calibration_method": calibration_method or "none",
            "features_used": features,
            "train_size": len(X_train),
            "test_size": len(X_test)
        }
    }

def main():
    print("🌲 Entraînement de référence avec Platt Scaling (Sigmoïde)...")
    results = train_and_evaluate(calibration_method='sigmoid')
    
    rf_metrics = results["rf_metrics"]
    xgb_metrics = results["xgb_metrics"]
    
    print("\n📈 --- RESULTATS (TEST SET) ---")
    print(f"🌲 Random Forest (Sigmoid) : Accuracy = {rf_metrics['accuracy']:.2%}, Brier Score = {rf_metrics['brier_score']:.4f}, Log Loss = {rf_metrics['log_loss']:.4f}")
    print(f"🚀 XGBoost (Sigmoid)       : Accuracy = {xgb_metrics['accuracy']:.2%}, Brier Score = {xgb_metrics['brier_score']:.4f}, Log Loss = {xgb_metrics['log_loss']:.4f}")
    
    # Choix automatique du meilleur modèle basé sur le Brier Score (le plus bas est le mieux)
    best_model_name = "RandomForestCalibrated" if rf_metrics['brier_score'] <= xgb_metrics['brier_score'] else "XGBoostCalibrated"
    best_metrics = rf_metrics if best_model_name == "RandomForestCalibrated" else xgb_metrics
    best_model_file = "rf_v1.joblib" if best_model_name == "RandomForestCalibrated" else "xgb_v1.joblib"
    
    print(f"\n🏆 Meilleur modèle sélectionné : {best_model_name} (Brier Score = {best_metrics['brier_score']:.4f})")
    
    # Sauvegarde des artefacts de référence
    print("\n💾 Sauvegarde des modèles dans ml/models/...")
    joblib.dump(results["rf_model"], MODELS_DIR / "rf_v1.joblib")
    joblib.dump(results["xgb_model"], MODELS_DIR / "xgb_v1.joblib")
    joblib.dump(results["label_encoder"], MODELS_DIR / "label_encoder_v1.joblib")
    
    with open(MODELS_DIR / "classes.txt", "w") as f:
        for c in results["label_encoder"].classes_:
            f.write(f"{c}\n")
            
    # Metadata MLOps JSON
    metadata = results["metadata"]
    metadata["models"] = {
        "RandomForestCalibrated": {
            "version": "v1",
            "file": "rf_v1.joblib",
            "metrics": rf_metrics
        },
        "XGBoostCalibrated": {
            "version": "v1",
            "file": "xgb_v1.joblib",
            "metrics": xgb_metrics
        }
    }
    metadata["chosen_production_model"] = best_model_name
    
    with open(MODELS_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("✅ Sauvegarde terminée avec succès !")

if __name__ == "__main__":
    main()
