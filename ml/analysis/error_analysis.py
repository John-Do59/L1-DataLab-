import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def run_error_analysis():
    print("🔬 Analyse Scientifique des Erreurs (Saison 2024/25)...")
    
    df = pd.read_csv(PROJECT_ROOT / "ml" / "features" / "ml_dataset.csv").dropna(subset=['result'])
    
    features = [
        'home_elo', 'away_elo', 'elo_diff',
        'home_form_5', 'away_form_5',
        'home_avg_overall', 'away_avg_overall',
        'home_squad_value', 'away_squad_value',
        'odds_prob_home', 'odds_prob_draw', 'odds_prob_away'
    ]
    
    le = LabelEncoder()
    df['target'] = le.fit_transform(df['result'])
    
    test_mask = df['season'] == '2024/25'
    X_train, y_train = df[~test_mask][features].fillna(0), df[~test_mask]['target']
    X_test, y_test = df[test_mask][features].fillna(0), df[test_mask]['target']
    
    model = xgb.XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_true = y_test
    
    # Matrice de Confusion
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    df_cm = pd.DataFrame(cm_norm, index=le.classes_, columns=le.classes_)
    
    print("\n📉 MATRICE DE CONFUSION (Normalisée) :")
    print(df_cm.round(2))
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(df_cm, annot=True, cmap='Blues', fmt='.2f')
    plt.title('Matrice de Confusion Normalisée (Saison 2024/25)')
    plt.xlabel('Prédiction')
    plt.ylabel('Vérité Terrain')
    plt.savefig(PROJECT_ROOT / 'ml' / 'analysis' / 'confusion_matrix.png')
    print(f"\n✅ Graphique sauvegardé dans ml/analysis/confusion_matrix.png")

if __name__ == "__main__":
    run_error_analysis()
