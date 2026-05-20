import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_DATA = PROJECT_ROOT / "ml" / "features" / "ml_dataset.csv"
UPCOMING_DATA = PROJECT_ROOT / "ml" / "features" / "ml_upcoming.csv"

def run_prediction():
    if not TRAIN_DATA.exists() or not UPCOMING_DATA.exists():
        print("❌ Datasets manquants. Lancez d'abord create_ml_dataset.py")
        return

    # 1. Chargement et Entraînement
    print("🧠 Entraînement du modèle XGBoost Optimisé (avec Elo)...")
    df_train = pd.read_csv(TRAIN_DATA)
    
    features = [
        'home_elo', 'away_elo', 'elo_diff',
        'home_form_5', 'away_form_5',
        'home_offensive_str', 'away_offensive_str',
        'home_defensive_str', 'away_defensive_str',
        'home_avg_overall', 'away_avg_overall',
        'home_squad_value', 'away_squad_value',
        'odds_prob_home', 'odds_prob_draw', 'odds_prob_away'
    ]
    
    # Nettoyage
    df_train = df_train.dropna(subset=['result'])
    df_train[features] = df_train[features].fillna(df_train[features].median())
    
    le = LabelEncoder()
    y_train = le.fit_transform(df_train['result'])
    X_train = df_train[features]

    # Hyperparamètres optimisés (basés sur le notebook 06)
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.02,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='multi:softprob',
        random_state=42
    )
    model.fit(X_train, y_train)

    # 2. Inférence
    df_upcoming = pd.read_csv(UPCOMING_DATA)
    if len(df_upcoming) == 0:
        print("✅ Aucun match à venir trouvé.")
        return

    df_upcoming[features] = df_upcoming[features].fillna(df_train[features].median())
    X_upcoming = df_upcoming[features]
    
    probs = model.predict_proba(X_upcoming)
    classes = le.classes_ # ['A', 'D', 'H']
    
    print("\n" + "="*85)
    print(f"{'DOMICILE':<25} | {'EXTÉRIEUR':<25} | {'ELO DIFF':<10} | {'PRONOSTIC (%)'}")
    print("-" * 85)
    
    for i, (_, row) in enumerate(df_upcoming.iterrows()):
        p = probs[i]
        prob_dict = dict(zip(classes, p))
        
        home = row['home_team']
        away = row['away_team']
        diff = row['elo_diff']
        
        print(f"{home:<25} | {away:<25} | {diff:>+10.1f} | H:{prob_dict['H']:.1%} D:{prob_dict['D']:.1%} A:{prob_dict['A']:.1%}")
    print("="*85 + "\n")

if __name__ == "__main__":
    run_prediction()
