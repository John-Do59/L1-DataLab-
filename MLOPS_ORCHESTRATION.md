# 🚀 Orchestration MLOps & Cycle de Vie du Modèle — Ligue 1 DataLab

Ce document détaille l'analyse fonctionnelle et technique du système d'orchestration continue (**MLOps**) appliqué au projet de prédiction des matchs de Ligue 1. Pour éviter l'obsolescence rapide d'un modèle prédictif dans le football, ce système est conçu comme un pipeline de données et de modèle en boucle fermée.

---

## 🎯 1. La Problématique de l'Obsolescence dans le Football

Un modèle de prédiction sportive est par nature **extrêmement sensible à la dérive temporelle** (*concept drift* et *data drift*). Si le système n'est pas alimenté après chaque journée de championnat, ses prédictions perdent rapidement toute valeur.

### Ce qu'il faut mettre à jour à chaque journée

* **Nouveaux résultats** : Les scores réels des matchs joués pour recalculer les statistiques globales.
* **Classement dynamique** : Les positions, points et dynamique générale au sein de la Ligue 1.
* **Forme récente (Momentum)** : Les performances sur une fenêtre glissante (généralement les 5 derniers matchs), calculées séparément pour le général, le domicile et l'extérieur.
* **Buts marqués & encaissés** : Indicateurs clés de l'efficacité offensive et défensive (Moyennes mobiles).
* **xG (Expected Goals)** : Si disponibles, ils permettent de décorréler le score final du volume d'occasions réelles (indicateur de chance/réussite).
* **Blessures / Suspensions** : Indispensables pour évaluer la baisse potentielle de performance d'un effectif.
* **Statistiques Domicile / Extérieur** : L'avantage du terrain reste l'un des prédicteurs les plus stables du football européen.

---

## 🏗️ 2. Architecture Globale du Pipeline MLOps

Le schéma ci-dessous illustre comment le flux de données alimente la base de données, traverse le pipeline de transformation, entraîne et compare les modèles, puis sert les prédictions en production sans interruption de service.

```mermaid
graph TD
    subgraph A. Ingestion & Ingestion Continue (ETL)
        A1[API Football / Scrapers] -->|Données de Match & Cotes| B[(PostgreSQL db-ml)]
    end
    
    subgraph B. Feature Engineering Automatique
        B -->|SQLAlchemy| C[ml/features/compute_elo.py]
        B -->|SQLAlchemy| D[ml/features/create_ml_dataset.py]
        C -->|Scores Elo Historiques & Temps Réel| E[match_elos.csv]
        D -->|Génération de la matrice de features| F[ml_dataset.csv]
    end
    
    subgraph C. Audit Qualité & Sécurité
        F --> G[validate_data_quality.py]
    end
    
    subgraph D. Entraînement & Calibration (Champion vs Challenger)
        G -->|Données Validées| H[train_models.py]
        H -->|Entraînement Random Forest / XGBoost| I[Calibration : Platt vs Isotonic]
        I -->|Calcul du Brier Score & Accuracy| J{Comparaison : Challenger vs Champion}
    end
    
    subgraph E. Hot Reloading & Serving API
        J -->|Challenger Meilleur| K[Promotion : Copie vers champion/ & Mise à jour de metadata.json]
        J -->|Challenger Rejeté| L[Conservation du Champion Actuel]
        K -->|Déploiement à chaud / 10ms| M[FastAPI Serving API]
        M -->|Explicabilité Proxy SHAP| N[Vue.js Frontend - AI Insights]
    end
    
    style J fill:#f9f,stroke:#333,stroke-width:2px
    style K fill:#9f9,stroke:#333,stroke-width:2px
```

---

## 🔄 3. Le Pipeline Continu Étape par Étape

L'orchestration est centralisée dans le script **`ml/pipeline.py`**. Il orchestre séquentiellement 6 phases critiques :

### Étape 1 : L'Update Ingestion & ETL (`scripts/run_etl.py`)

Le pipeline commence par lancer le scraper/client d'API. Il récupère les nouveaux résultats de la journée écoulée, les cotes associées, ainsi que les informations de valeur marchande, puis effectue un mapping robuste des équipes pour insérer ces données propres dans PostgreSQL.

### Étape 2 : Le Feature Engineering Automatique (`compute_elo.py` & `create_ml_dataset.py`)

Pour maximiser la performance des modèles, des features avancées et dynamiques sont calculées à chaud :

1. **Évaluation ELO** : Calculée de manière récursive sur l'historique complet pour attribuer un score de force intrinsèque à chaque équipe.
2. **Statistiques glissantes** : Calcul des buts moyens marqués/encaissés, clean sheets, forme récente sur 5 matchs (nombre de points cumulés), et historique des confrontations directes (**H2H**).

### Étape 3 : Le Réentraînement Automatique des Challengers

Le script d'entraînement s'exécute pour générer plusieurs configurations de modèles (Random Forest et XGBoost) combinées à deux types de calibration :

* **Platt Scaling (Sigmoïde)** : Idéal lorsque le biais est linéaire.
* **Isotonic Regression** : Plus souple et puissant sur de grands volumes.

```python
# Extrait conceptuel de la calibration et de la sauvegarde
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
import joblib

# Entraînement du modèle de base
base_model = RandomForestClassifier(n_estimators=100, random_state=42)
base_model.fit(X_train, y_train)

# Calibration des probabilités (Platt Scaling)
calibrated_model = CalibratedClassifierCV(estimator=base_model, method="sigmoid", cv="prefit")
calibrated_model.fit(X_val, y_val)

# Sauvegarde temporaire du Challenger
joblib.dump(calibrated_model, "ml/models/archive/rf_challenger.joblib")
```

### Étape 4 : La Confrontation Champion vs Challenger

Le système ne déploie jamais aveuglément un nouveau modèle. Il effectue un audit de performance rigoureux en comparant le **Brier Score** (la métrique de calibration cruciale en football) du nouveau **Challenger** face au **Champion** actuellement en production :

$$\text{Brier Score} = \frac{1}{N} \sum_{i=1}^{N} \sum_{j=1}^{C} (p_{ij} - y_{ij})^2$$

* Si le Challenger améliore significativement le Brier Score (seuil de gain $\ge 0.002$), il est **promu**.
* Sinon, il est archivé et le Champion actuel reste actif en production.

### Étape 5 : Versioning des Modèles (`ml/models/metadata.json`)

Chaque promotion écrit le modèle et son encodeur dans le registre `/archive` avec un identifiant unique basé sur le timestamp (ex : `rf_v_20260520_012000.joblib`).
Le fichier centralisé **`metadata.json`** pointe à tout moment vers la version active et détaille ses métriques (Brier Score, Accuracy, Log Loss) et les features utilisées.

### Étape 6 : Hot Reloading sur FastAPI

L'API FastAPI ne nécessite aucun redémarrage physique pour charger le nouveau modèle. Elle lit de manière dynamique `metadata.json` ou surveille le dossier `champion/champion_model.joblib`. Lorsqu'une nouvelle version est détectée, le fichier est rechargé en mémoire instantanément ($\le 10$ ms), assurant un déploiement sans interruption de service (*Zero-Downtime*).

---

## 🛠️ 4. Rôle de SQLAlchemy et d'Alembic dans le MLOps

En production, **les features d'un modèle de Machine Learning évoluent constamment**. Un modèle simple peut commencer avec uniquement l'historique des buts, puis intégrer l'Elo, la possession moyenne, les expected goals (xG), la météo ou encore les blessures.

### SQLAlchemy : Le Pont entre les Données et le ML

* **Avant l'entraînement** : SQLAlchemy permet de formuler des requêtes complexes, robustes et typées pour assembler le dataset ML à partir de tables relationnelles.
* **Après la prédiction** : Il permet de persister en base les prédictions générées par l'API, les probabilités associées (Victoire/Nul/Défaite) ainsi que les métriques réelles pour détecter les dérives futures.

### Alembic : Le Gardien du Schéma de Données

Chaque nouvelle feature ML nécessite souvent une modification structurelle de la base de données PostgreSQL. **Alembic** automatise et historise ces modifications de schéma sans perte de données.

#### Workflow Opérationnel de Migration MLOps

1. **Nouvelle feature identifiée** : Vous ajoutez une colonne dans vos modèles SQLAlchemy (ex : les xG domicile).

   ```python
   # db/models.py
   class Match(Base):
       __tablename__ = "matches"
       id = Column(Integer, primary_key=True)
       # ... autres colonnes ...
       xg_home = Column(Float, nullable=True) # Nouvelle feature ML
   ```

2. **Génération de la migration** : Alembic compare vos modèles Python avec la base de données réelle et génère le fichier de migration.

   ```bash
   alembic revision --autogenerate -m "add xg features to matches"
   ```

3. **Application en production** : Le schéma de la base de données est mis à jour de manière sécurisée.

   ```bash
   alembic upgrade head
   ```

Sans Alembic, faire évoluer un modèle en production devient extrêmement risqué, provoquant des erreurs d'insertion de données ou des incompatibilités majeures de format (écrans blancs côté frontend, crashs de l'API FastAPI).

---

## 🚀 5. La Stack Technique Recommandée pour Ligue 1 DataLab

Pour concrétiser pleinement ce workflow MLOps de pointe, voici la stack moderne intégrée au projet :

| Technologie | Rôle dans le Projet |
| :--- | :--- |
| **FastAPI** | API d'inférence ultra-rapide, asynchrone, documentée avec Swagger (OpenAPI) par défaut. |
| **SQLAlchemy** | ORM pour manipuler les données de matchs comme des objets Python typés. |
| **Alembic** | Gestionnaire de migrations SQL robuste pour faire évoluer le schéma de features en production. |
| **PostgreSQL** | Base de données relationnelle puissante stockant l'historique des matchs et des cotes. |
| **Pandas / Numpy** | Manipulation de données et calcul vectoriel des statistiques glissantes. |
| **XGBoost & Scikit-Learn** | Modèles de Gradient Boosting et Forêt Aléatoire calibrés pour la classification multi-classe. |
| **MLflow (ou Registry Interne)** | Tracking rigoureux des hyperparamètres, versions de modèles et métriques d'évaluation. |
| **Docker & Compose** | Isolation complète de l'API FastAPI, de PostgreSQL et du monitoring dans des conteneurs légers. |
| **Grafana & Prometheus** | Monitoring continu de la dérive de prédiction (*Concept Drift*) et des RED metrics de l'API. |

---

> 💡 **En résumé** : En liant un scraper automatique à une base PostgreSQL gérée par **SQLAlchemy/Alembic**, en réentraînant le modèle sur un protocole **Champion-Challenger (Brier Score)**, et en chargeant dynamiquement le modèle dans **FastAPI**, vous obtenez une véritable usine d'IA industrielle, résiliente et immunisée contre l'obsolescence.
