# Plan d'Implémentation - L1 DataLab

Ce plan détaille les étapes pour mettre en place la plateforme L1 DataLab, en commençant par l'ingestion des données (scraping) et le socle technique.

## User Review Required

> [!IMPORTANT]
> Nous devons confirmer la source de données exacte (URL) pour le scraping afin d'ajuster les sélecteurs et la logique de navigation.

> [!WARNING]
> L'utilisation d'Ollama nécessite des ressources locales significatives (GPU). Nous devrons valider la configuration de votre machine pour l'inférence locale.

## Open Questions

1.  **Source de données** : Quel est le site que vous souhaitez scraper ? (ex: `ligue1.fr`, `fbref.com`, `transfermarkt.fr`).
2.  **Fréquence de mise à jour** : Les données doivent-elles être rafraîchies quotidiennement ou après chaque journée de championnat ?
3.  **Volume historique** : Sur combien de saisons passées souhaitez-vous récupérer des données pour l'entraînement du modèle ML ?

## Proposed Changes

### Phase 1 : Initialisation & Socle Core

Mise en place de l'environnement de développement et des services transverses.

#### [NEW] [services/core](file:///Users/amaury/L1-DataLab-/services/core)
- Initialisation du package `core` avec Pydantic pour la configuration.
- Configuration du logging structuré (JSON) pour Loki.
- Setup de base d'OpenTelemetry pour l'instrumentation automatique.

#### [NEW] [docker-compose.yml](file:///Users/amaury/L1-DataLab-/docker-compose.yml)
- Services de base : PostgreSQL (l1_ml, l1_app), Redis (caching), Ollama.
- Stack monitoring : Prometheus, Grafana, Loki.

---

### Phase 2 : Ingestion de Données (Scraper)

Développement du pipeline ETL pour alimenter la base `l1_ml`.

#### [NEW] [services/scraper](file:///Users/amaury/L1-DataLab-/services/scraper)
- Création du projet Scrapy ou scripts Selenium/Playwright (selon le site cible).
- Modèles Pydantic pour valider les données scrapées avant insertion.
- Pipelines SQLAlchemy pour l'insertion asynchrone dans PostgreSQL.

---

### Phase 3 : Modèle ML & API ML

Préparation des données et premier service de prédiction.

#### [NEW] [ml/](file:///Users/amaury/L1-DataLab-/ml)
- Notebooks d'exploration (EDA) sur les données collectées.
- Scripts de feature engineering (forme des équipes, historiques H2H).
- Entraînement d'un premier modèle (RandomForest ou XGBoost).

#### [NEW] [apps/l1-ml-api](file:///Users/amaury/L1-DataLab-/apps/l1-ml-api)
- Endpoint `/predict` pour consommer le modèle.
- Instrumentation OpenTelemetry pour mesurer la latence d'inférence.

---

### Phase 4 : API Produit & RAG

Développement de la façade applicative et de l'assistant intelligent.

#### [NEW] [apps/l1-app-api](file:///Users/amaury/L1-DataLab-/apps/l1-app-api)
- Endpoints REST pour le frontend.
- Intégration du composant RAG pour répondre aux questions sur les stats.

---

### Phase 5 : Frontend & Observabilité Finale

Dashboarding et monitoring.

#### [NEW] [monitoring/](file:///Users/amaury/L1-DataLab-/monitoring)
- Configuration des dashboards Grafana (Business & Tech).
- Règles d'alerting (Alertmanager).

## Verification Plan

### Automated Tests
- Tests unitaires pour les parsers du scraper (`pytest`).
- Validation des schémas de données avec Pydantic.
- Tests d'intégration pour les endpoints API (`TestClient`).

### Manual Verification
- Vérification du bon stockage des données dans PostgreSQL via DBeaver ou CLI.
- Test de la boucle RAG avec des questions complexes sur la Ligue 1.
- Vérification de la remontée des traces dans Grafana Tempo/Loki.
