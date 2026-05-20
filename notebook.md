# 📓 Guide des Notebooks L1 DataLab

Ce document sert de cartographie pour comprendre l'exploration de données et la modélisation prédictive de Ligue 1 au sein de ce projet. Nos notebooks sont organisés de manière modulaire dans le répertoire [ml/notebooks/](file:///Users/amaury/L1-DataLab-/ml/notebooks).

## 📋 Liste des Notebooks

### [01 — EDA Ligue 1](file:///Users/amaury/L1-DataLab-/ml/notebooks/01_eda_ligue1.ipynb) (Exploratory Data Analysis)
*   **Rôle** : Analyse exploratoire approfondie de l'historique des matchs.
*   **Contenu** : 
    *   Distribution des résultats (Home Win, Draw, Away Win) et mise en évidence de l'avantage à domicile historique (~45% de victoires à domicile).
    *   Évolution de la moyenne de buts marqués par match.
    *   Analyse de corrélation initiale entre les caractéristiques de base.

### [02 — Feature Engineering](file:///Users/amaury/L1-DataLab-/ml/notebooks/02_feature_engineering.ipynb)
*   **Rôle** : Création et enrichissement des variables prédictives.
*   **Contenu** : 
    *   Calcul de la forme dynamique (`form_5`) basée sur les points glissants des 5 derniers matchs.
    *   Calcul de la force offensive et défensive glissante.
    *   Préparation et normalisation des valeurs marchandes et scores FIFA Overall.

### [03 — Comparaison de Modèles & MLOps](file:///Users/amaury/L1-DataLab-/ml/notebooks/03_model_comparison.ipynb)
*   **Rôle** : Le benchmark scientifique majeur de ce projet.
*   **Contenu** : 
    *   **Split Temporel** : Division des données 80% passées (train) / 20% futures (test) pour éviter le *data leakage* stochastique.
    *   **Entraînement & Calibration** : Entraînement de XGBoost Classifier vs Random Forest Calibré (`CalibratedClassifierCV`).
    *   **Matrices de Confusion** : Analyse fine des erreurs par classe (Vitoire Domicile, Nul, Extérieur).
    *   **SHAP Analysis** : Interprétabilité locale et globale pour identifier quelles variables (Elo, cotes, valeurs de l'effectif) influencent les prédictions.

---

## 🛠️ Comment Exécuter les Notebooks en Local ?

1.  **Activer l'environnement virtuel** :
    ```bash
    source .venv/bin/activate
    ```
2.  **Lancer l'interface Jupyter** :
    ```bash
    jupyter notebook
    # Ou ouvrez directement le dossier dans VS Code avec l'extension Jupyter
    ```
3.  **Sélectionner le noyau (Kernel)** :
    Sélectionnez le noyau de l'environnement virtuel `.venv` pour garantir que toutes les dépendances (dont `shap`, `xgboost` et `scikit-learn`) sont correctement chargées.

