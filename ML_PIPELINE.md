# 🧠 Ligue 1 Predictive Analytics - Guide du Machine Learning

Ce document détaille l'implémentation de l'intelligence artificielle pour la prédiction des résultats de la Ligue 1 (H/D/A).

## 🚀 1. Architecture du Pipeline ML

Le projet suit une approche itérative et modulaire :
1. **Extraction** : Scraping API Ligue 1 (avec `DuplicatesPipeline` pour filtrage à la source) + Données Historiques Kaggle.
2. **Ingestion** : Stockage PostgreSQL et normalisation (Mapping des équipes).
3. **Feature Engineering** : Calcul des statistiques glissantes (rolling) et des scores Elo.
4. **Modélisation** : Progression de la Régression Logistique vers XGBoost Optimisé.
5. **Analyse Critique** : Étude des erreurs et calibration des probabilités.

---

## 📊 2. Le Coeur du Signal : Les Features
Notre modèle s'appuie sur quatre piliers de données :

- **Elo Rating (Dynamique)** : Système de notation de la puissance relative des équipes calculé sur 20 ans d'historique.
- **Forme Récente (Momentum)** : Moyenne des points et buts sur les 5 derniers matchs.
- **Valeur Marchande (Financier)** : Données Transfermarkt et notes FC24 pour quantifier le talent brut.
- **Marché du Pari (Cotes)** : Intégration des probabilités implicites des bookmakers (Pinnacle, B365).

---

## 📓 3. Suite des Notebooks (Parcours Pédagogique)

Les notebooks dans `ml/notebooks/` documentent la recherche :
1. `01_data_exploration.ipynb` : EDA et validation des hypothèses (Avantage domicile, corrélations).
2. `02_feature_engineering.ipynb` : Transformation des données brutes en features ML.
3. `03_baseline_logistic.ipynb` : Modèle de base linéaire.
4. `04_random_forest.ipynb` : Introduction de la non-linéarité.
5. `05_xgboost.ipynb` : Modèle de Gradient Boosting standard.
6. `06_optimized_xgboost.ipynb` : Modèle final avec **Elo Rating** et hyperparamètres tunés (**Accuracy: 48.04%**).

---

## 🛠️ 4. Commandes pour Exécuter le Projet

### A. Préparation des données (ETL)
```bash
# Activation de l'environnement
source .venv/bin/activate

# Ingestion des données Ligue 1 et Betting
python scripts/etl_step3_api.py
python scripts/etl_step4_betting.py
```

### B. Génération des Features & Elo
```bash
# Calcul des scores Elo historiques
python ml/features/compute_elo.py

# Création du dataset final pour l'entraînement
python ml/features/create_ml_dataset.py
```

### C. Prédictions Live (Saison 2025/2026)
```bash
# Lancer les pronostics pour les prochains matchs
python ml/training/predict_upcoming.py
```

---

## 🔬 5. Analyse de Performance (Saison 2024/25)
- **Accuracy Globale** : ~48% à 52% (selon le tuning).
- **Home Win Recall** : ~81% (Forte capacité à identifier les victoires à domicile).
- **Draw Recall** : ~13% (Le match nul reste la zone de plus grande incertitude du football).

---
✨ *Projet développé dans le cadre d'une soutenance RNCP — Ingénierie de la donnée et Intelligence Artificielle.*
