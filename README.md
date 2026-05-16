# ⚽ Ligue 1 DataLab - Predictive Analytics

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost-orange.svg)](https://xgboost.readthedocs.io/)

Plateforme industrielle de collecte et de prédiction des résultats de la Ligue 1 McDonald’s. Ce projet combine **Web Scraping**, **Ingénierie de données SQL** et **Machine Learning** pour prédire l'issue des matchs de football.

## 🌟 Points Forts
- **Pipeline ETL Automatisé** : Ingestion multi-sources (API Ligue 1, Kaggle, Transfermarkt).
- **Intelligence Artificielle** : Modèle XGBoost optimisé intégrant un système d'**Elo Rating** dynamique.
- **Scraping Live** : Récupération en temps réel des matchs de la saison 2025/2026.
- **Analyse Scientifique** : Évaluation rigoureuse des biais et des limites prédictives.

## 🏗️ Infrastructure
- **Scraping** : Scrapy (Ligue 1 API).
- **Base de données** : PostgreSQL (Architecture Micro-DBs).
- **ML** : XGBoost Optimisé + Elo Rating System.
- **Infrastructure** : Docker Compose (Microservices).
- **Backend** : FastAPI + SQLAlchemy 2.0 Async + Pydantic v2.

## 📚 Documentation Technique

Pour approfondir le fonctionnement du système, consultez nos guides détaillés :
- 🗄️ [SQLAlchemy 2.0 Async](docs/SQLALCHEMY.md) : Gestion de la base de données asynchrone.
- ✅ [Pydantic V2](docs/PYDANTIC.md) : Validation et typage des données.
- ⚙️ [Alembic](docs/ALEMBIC.md) : Gestion des migrations et du schéma.
- 🧪 [Guide de Test](docs/TESTS.md) : Commandes pour valider le système distribué.
- 🐳 [Docker Guide](DOCKER.md) : Orchestration et optimisation des images.

## 🚀 Installation & Lancement (Production)

Pour lancer l'ensemble de la plateforme (APIs + Bases de données) :

```bash
docker compose up -d
```

Les services seront disponibles sur :
- **App API** : [http://localhost:8002](http://localhost:8002)
- **ML API** : [http://localhost:8001](http://localhost:8001)
- **Frontend** : [http://localhost:5173](http://localhost:5173)

Pour plus de détails, consultez [DOCKER.md](./DOCKER.md) et [ML_PIPELINE.md](./ML_PIPELINE.md).

## 📂 Structure du Projet
- `db/` : Schémas SQL et scripts d'initialisation PostgreSQL.
- `app-api/` : API principale FastAPI (Authentification JWT, Utilisateurs, Historique)
- `frontend/` : Interface Vue.js 3 "Sunset Mystique" (GSAP, Tailwind v4, Liquidglass)
- `scraper/` : Extraction Scrapy pour extraire les données de Ligue1.com.
- `scripts/` : Pipeline d'ETL et outils de maintenance.
- `ml/` : 
    - `features/` : Scripts de calcul d'Elo et de feature engineering.
    - `notebooks/` : Suite complète d'analyse et de modélisation (01 à 06).
    - `training/` : Scripts d'entraînement et d'inférence live.

## 🚀 Démarrage Rapide
Pour comprendre et exécuter le pipeline de Machine Learning, consultez le guide dédié :
👉 **[Guide du Machine Learning (ML_PIPELINE.md)](./ML_PIPELINE.md)**

## 📊 Résultats
Le modèle final atteint une **Accuracy de 48.04%** sur la saison en cours, avec une excellente capacité de détection des victoires à domicile (**81% de recall**).

---
*Projet réalisé pour la validation du titre RNCP.*
