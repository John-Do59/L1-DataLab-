# L1 DataLab ⚽

L1 DataLab est une plateforme d’analyse et de prédiction pour le championnat de France de football (Ligue 1). Conçue comme un produit **production‑ready**, elle intègre des pipelines de données, du machine learning, des APIs modernes, un assistant IA local (RAG) et une stack d'observabilité complète.

## 🚀 Vision du Projet

L'objectif est de fournir aux analystes et aux passionnés des outils avancés pour :
- **Prédire** l'issue des matchs à partir de données historiques.
- **Visualiser** les statistiques clés via un dashboard interactif.
- **Explorer** les données grâce à un assistant IA local basé sur le RAG (Retrieval-Augmented Generation).
- **Monitorer** la santé du système en temps réel (Traces, Métriques, Logs).

## 🏗️ Architecture Technique

Le projet suit une architecture multi-services conteneurisée :

- **Frontend** : Vue.js (L1 DataLab Studio)
- **Backend APIs** : FastAPI (App API & ML API)
- **Data & ML** : Scrapy, Scikit-learn, PostgreSQL (pgvector)
- **IA Locale** : Ollama (Qwen) + LangChain
- **Observabilité** : OpenTelemetry, Prometheus, Grafana, Loki, Alertmanager

Pour plus de détails, consultez :
- 📄 [brief.md](./brief.md) : Vision et objectifs business.
- 📄 [architecture.md](./architecture.md) : Structure technique et organisation des dossiers.
- 📄 [requirements-txt.md](./requirements-txt.md) : Gestion des dépendances.

## 🛠️ Installation

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/John-Do59/L1-DataLab-.git
   cd L1-DataLab-
   ```

2. **Créer l'environnement virtuel** :
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt -r requirements-ml.txt -r requirements-dev.txt -r requirements-monitoring.txt
   ```

4. **Configurer l'environnement** :
   ```bash
   cp .env.example .env
   ```

## 📊 Observabilité

La plateforme est entièrement instrumentée avec OpenTelemetry. Vous pouvez accéder aux dashboards de monitoring une fois la stack lancée via Docker Compose :
- **Grafana** : Visualisation des métriques et logs.
- **Prometheus** : Collecte des métriques.
- **Loki** : Centralisation des logs.

## 🤝 Contribution

Ce projet a été structuré pour répondre aux exigences pédagogiques du RNCP, avec une séparation stricte des responsabilités et une documentation complète.
