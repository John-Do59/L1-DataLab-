# Phase 3 : Exploration et Modélisation (Machine Learning)

Ce document décrit l'architecture et la méthodologie de la phase "Data Science" du projet L1 DataLab.
Après avoir ingéré, nettoyé et fusionné les données (Data Engineering/ETL), nous entrons dans la phase d'exploration (EDA) et de modélisation prédictive.

## 🏗️ Architecture ML
La logique Machine Learning est isolée du reste du projet pour respecter les standards de l'industrie :

```text
ml/
├── notebooks/                   # Exploration scientifique (Jupyter)
│   ├── 01_data_exploration.ipynb  # Analyse univariée/bivariée, corrélations
│   ├── 02_feature_engineering.ipynb
│   ├── 03_baseline_logistic.ipynb # Régression Logistique naïve
│   ├── 04_random_forest.ipynb     # Modèle non-linéaire (Baseline avancée)
│   └── 05_xgboost.ipynb           # Gradient Boosting (Optimisation)
├── features/                    # Datasets générés par l'ETL (ex: ml_dataset.csv)
├── training/                    # Scripts Python d'industrialisation des modèles
└── models/                      # Modèles sérialisés (.joblib, .pkl) prêts pour l'inférence
```

## 🧠 Stratégie d'Exploration (EDA)
Le notebook `01_data_exploration.ipynb` sert à valider le *feature engineering* avant de lancer des modèles complexes.
Il répond aux questions critiques :
1. **Les features discriminent-elles les classes (H/D/A) ?** Analyse des distributions (ex: l'équipe à domicile gagne-t-elle plus souvent quand `home_squad_value` est très élevé par rapport à l'extérieur ?).
2. **Quelles sont les corrélations ?** Détection de la multicolinéarité (features redondantes) et des signaux forts.
3. **Existe-t-il du *Data Leakage* ?** Vérification que les features ne contiennent pas d'information du futur.

## 🚀 Évolution de la Modélisation
L'approche choisie est **incrémentale**, indispensable pour construire un socle robuste et explicable pour un portfolio RNCP :

### 1. Régression Logistique (Le modèle "Naïf")
- **But** : Établir une *baseline* absolue.
- **Résultat** : En raison du déséquilibre structurel du football (Avantage Domicile fort, Nuls très difficiles à prédire), ce modèle tend à converger vers la prédiction systématique de la classe majoritaire (H). Il ne capte pas les relations non-linéaires complexes.

### 2. Random Forest (La Baseline Non-Linéaire)
- **But** : Gérer les interactions de features complexes sans overfitter facilement.
- **Approche** : Utilisation de `class_weight="balanced"` pour forcer le modèle à prêter attention aux matchs Nuls (D) et aux victoires à l'Extérieur (A).
- **Résultat** : ~41.5% d'accuracy sur la saison live.
- **Analyse** : Étude de la *Feature Importance* (ex: vérifier si les cotes des bookmakers dominent la capacité prédictive des formes des équipes).

### 3. XGBoost (L'Optimisation Finale)
- **But** : Capturer des relations non-linéaires fines et maximiser la précision globale.
- **Approche** : Hyperparameter tuning et gestion du gradient boosting.
- **Résultat** : **45.42% d'accuracy** sur la saison 2024/25.
- **Observation** : Le modèle XGBoost surpasse significativement les baselines linéaires et le Random Forest, montrant une réelle capacité à prédire les victoires à l'extérieur (Recall ~18% sur A vs ~50% sur H).

## 🏁 Conclusion Comparative
| Modèle | Accuracy (Test 2024/25) | F1-Score | Statut |
| :--- | :---: | :---: | :--- |
| Régression Logistique | ~39% | ~31% | Baseline |
| Random Forest | ~41.5% | ~39% | Validé |
| **XGBoost** | **45.42%** | **40.3%** | **Production-Ready** |

> [!IMPORTANT]
> Le succès de ce pipeline repose sur la **qualité de l'ETL**. La correction du bug de mapping des IDs d'équipes a permis d'injecter les **cotes bookmakers**, propulsant ainsi la capacité prédictive du modèle.
