# ⚽ Ligue 1 DataLab - Predictive Analytics

![Ligue 1 AI Banner](services/frontend/src/assets/backgrounds/ballon-ia5.png)

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

### Guides d'implémentation (racine)

| Document | Description |
|----------|-------------|
| [design.md](design.md) | Stratégie produit, DA Sunset Mystique, tokens |
| [FRONTEND-PLAN.md](FRONTEND-PLAN.md) | Roadmap & architecture frontend |
| [frontend-implementation.md](frontend-implementation.md) | Theme system, logos, vues, branches |
| [backend-implementation.md](backend-implementation.md) | App API, auth, predict, ML |
| [rag-implementation.md](rag-implementation.md) | Oracle RAG, SSE, pgvector, mood |

### Références techniques

- 🗄️ [SQLAlchemy 2.0 Async](docs/SQLALCHEMY.md)
- ✅ [Pydantic V2](docs/PYDANTIC.md)
- ⚙️ [Alembic](docs/ALEMBIC.md)
- 🧪 [Guide de Test](docs/TESTS.md)
- 🐳 [Docker Guide](DOCKER.md)

## 🚀 Installation & Lancement (Production)

Pour lancer l'ensemble de la plateforme (APIs + Bases de données) :

```bash
docker compose up -d
```

Les services seront disponibles sur :

- **App API** : [http://localhost:8002](http://localhost:8002)
- **ML API** : [http://localhost:8001](http://localhost:8001)
- **Frontend** : [http://localhost:8080](http://localhost:8080) (Docker) ou `:5173` (Vite dev)

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
