# L1 DataLab – Plateforme IA Ligue 1 production‑ready

## Vision du projet
L1 DataLab est une plateforme d’analyse et de prédiction dédiée au championnat de première division française, conçue comme un produit production‑ready : pipelines data, machine learning, APIs, frontend, RAG local et observabilité complète (OpenTelemetry, Prometheus, Grafana, Loki, Alertmanager).

**Objectifs principaux :**
*   Prédire l’issue des matchs de première division française à partir de données historiques.
*   Fournir une API exploitable (et potentiellement monétisable) pour la data et les prédictions.
*   Proposer un dashboard interactif pour visualiser statistiques et insights.
*   Intégrer un assistant IA local (RAG + LLM) pour expliquer et explorer les données.

## Cas d’usage métier
Analystes, médias, parieurs ou fans qui veulent :
*   visualiser les stats des matchs et équipes,
*   obtenir des prédictions sur les matchs à venir,
*   comprendre les facteurs clés via des explications IA.

Entreprises tech / data voulant un exemple de plateforme IA full stack :
*   ingestion multi‑sources,
*   ML,
*   APIs,
*   frontend,
*   MLOps + observabilité 3 piliers.

## Architecture fonctionnelle

### 1. Collecte & préparation des données
**Sources de données (exemples) :**
*   API de football (fixtures, résultats, classements).
*   Datasets publics d’historiques de matchs / statistiques (Kaggle ou open data).

**Pipeline data :**
*   Collecte automatique via Scrapy ou scripts API.
*   Nettoyage, transformation, agrégation de plusieurs sources.

**Stockage dans PostgreSQL :**
*   base `l1_ml` pour la partie ML,
*   base `l1_app` pour la partie applicative.

### 2. Machine Learning (L1 DataLab Core / ML API)
Modèle de classification ou régression, par exemple :
*   issue du match (victoire domicile / nul / victoire extérieur),
*   probabilité de victoire, nombre de buts.

**Pipeline ML :**
*   préparation des features,
*   split train/test,
*   entraînement, évaluation (accuracy, F1, etc.),
*   versioning des modèles et des métriques.

**ML API (FastAPI) :**
*   `POST /train` : enclenche un entraînement.
*   `GET /models` : liste les modèles / versions.
*   `POST /predict` : prédiction pour un match.
*   `GET /metrics` : métriques de performance ML.

### 3. API produit (L1 DataLab App API)
**App API (FastAPI)** consommée par le frontend et des clients externes :
*   Authentification / gestion utilisateurs.
*   Endpoints data : `GET /matches`, `GET /standings`, `GET /teams`, etc.
*   Endpoints prédictions : `GET /matches/{match_id}/prediction` (appel interne à l’API ML).
*   Endpoints insights / IA : `POST /insights/question` (appel interne au RAG).

**Base `l1_app` (PostgreSQL) :**
*   utilisateurs, profils, droits,
*   matchs, équipes, classements exposés au front,
*   historique de prédictions / interactions.

### 4. Frontend (L1 DataLab Studio)
**Application Vue.js (HTML/CSS/JS) :**
*   Dashboard des matchs (passés/à venir).
*   Visualisation des classements, formes récentes.
*   Affichage des prédictions pour les matchs à venir.
*   Page “Insights” pour interagir avec l’IA et voir des explications.

Le frontend ne parle qu’à l’App API, qui joue le rôle de façade produit.

### 5. RAG & IA locale (L1 DataLab RAG)
**Base de connaissances :**
*   résumés de matchs, statistiques agrégées, historiques de confrontations, descriptions.

**Stockage vectoriel avec pgvector (PostgreSQL).**

**LLM local via Ollama (ex. Qwen 2.5 7B) pour :**
*   répondre aux questions sur les stats et historiques,
*   expliquer les prédictions du modèle,
*   générer des insights textuels.

**Orchestration possible avec LangChain / LangGraph :**
*   outil de recherche vectorielle,
*   appels au modèle ML,
*   génération de réponses structurées.

## Architecture technique

### Services
*   `l1-ml-api` : FastAPI, service ML (+ endpoint `/metrics` + traces via OpenTelemetry).
*   `l1-app-api` : FastAPI, service produit (+ `/metrics` + traces via OpenTelemetry).
*   `l1-ml-db` : PostgreSQL (données ML).
*   `l1-app-db` : PostgreSQL (données applicatives).
*   `l1-rag` : composant RAG (intégré ou séparé).
*   `frontend` : application Vue.js.
*   `ollama` : service LLM local (Qwen).

### Observabilité & Ops

#### OpenTelemetry
Auto‑instrumentation des deux APIs FastAPI (App et ML) pour collecter :
*   traces : spans par requête (route, durée, statut),
*   métriques : latence, throughput, erreurs.
Utilisation de l’OTel Collector ou exporters pour :
*   envoyer les métriques vers Prometheus,
*   enrichir les logs avec des identifiants de trace (`trace_id`).

#### Prometheus
Collecte des métriques des services via OpenTelemetry / endpoint `/metrics`.
Séries de métriques suivies :
*   nombre de requêtes par endpoint / code HTTP,
*   latence,
*   erreurs,
*   métriques spécifiques ML (exposées par l’API ML).

#### Grafana
Dashboards pour :
*   L1 DataLab App API : trafic, latence, erreurs.
*   L1 DataLab ML API : temps de prédiction, volumétrie, erreurs.
*   Vue globale de la plateforme (santé des services, BDD).
Intégration des métriques Prometheus et des logs Loki.

#### Loki + Promtail
Centralisation des logs :
*   logs applicatifs des APIs FastAPI (App / ML / RAG),
*   logs système pertinents.
Requêtes des logs dans Grafana, corrélées avec les traces OpenTelemetry (via `trace_id` dans les logs) pour faciliter le debugging.

#### Alertmanager
Règles d’alerte basées sur les métriques Prometheus, par exemple :
*   taux d’erreur HTTP > X % sur 5 minutes,
*   indisponibilité d’un service (App ou ML API),
*   latence des prédictions au‑delà d’un seuil.
Envoi d’alertes via e‑mail / Slack / autre canal.

### Docker & CI/CD
**Docker / Docker Compose :**
*   un container par service (APIs, DBs, Ollama, Prometheus, Grafana, Loki, Promtail, Alertmanager, OTel Collector).

**CI/CD (GitHub Actions, GitLab CI ou autre) :**
*   exécution des tests backend (et éventuellement frontend),
*   build des images Docker,
*   push vers un registre,
*   déploiement sur un environnement (dev/stage/prod).

## Objectifs pédagogiques / RNCP
L1 DataLab permet de démontrer :

**Bloc données :**
*   collecte multi‑sources (API + datasets),
*   nettoyage, agrégation, stockage dans des BDD relationnelles,
*   exposition des données via API REST.

**Bloc IA / ML / MLOps :**
*   entraînement et évaluation d’un modèle de classification,
*   exposition du modèle via une API dédiée,
*   monitoring du modèle (métriques ML),
*   CI/CD du modèle et des services ML.

**Bloc application IA :**
*   conception d’une architecture multi‑services (App API, ML API, RAG, frontend),
*   développement d’un backend et d’un frontend Vue.js,
*   intégration d’un service IA (ML + RAG local),
*   mise en place d’une observabilité complète (traces, métriques, logs, alertes) avec OpenTelemetry, Prometheus, Grafana, Loki et Alertmanager.

## Pitch court (CV / portfolio)
L1 DataLab est une plateforme d’analyse et de prédiction IA pour le championnat de première division française.
Elle combine ingestion multi‑sources, machine learning pour prédire les résultats, RAG local avec LLM pour générer des insights, une API FastAPI exploitable, un frontend Vue.js, et une observabilité complète basée sur OpenTelemetry, Prometheus, Grafana, Loki et Alertmanager, le tout conteneurisé et orchestré via Docker et CI/CD.
