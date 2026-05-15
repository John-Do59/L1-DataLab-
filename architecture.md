# Architecture du Projet L1-DataLab

Ce document détaille la structure organisationnelle du projet L1 DataLab.

## Structure des Dossiers

```text
L1-DataLab/
│
├── apps/                        # Applications principales (FastAPI & Vue.js)
│   ├── frontend/                # Application Vue.js (L1 DataLab Studio)
│   ├── l1-app-api/              # API Produit (Façade client)
│   └── l1-ml-api/               # API Machine Learning (Inférence & Entraînement)
│
├── services/                    # Services métier et composants partagés
│   ├── scraper/                 # Scripts de collecte de données (Scrapy/Scripts)
│   ├── rag/                     # Composant Retrieval-Augmented Generation
│   └── core/                    # Code partagé (ex shared)
│       ├── config/              # Gestion des configurations (Pydantic settings)
│       ├── logging/             # Configuration des logs structurés
│       ├── observability/       # Setup OpenTelemetry & instrumentation
│       └── utils/               # Utilitaires communs
│
├── ml/                          # Pipeline Machine Learning
│   ├── features/                # Engineering et stockage des features
│   ├── training/                # Scripts d'entraînement des modèles
│   └── models/                  # Modèles sérialisés et versioning
│
├── data/                        # Stockage des fichiers de données brutes et traitées
│
├── db/                          # Schémas, migrations et scripts de base de données
│
├── monitoring/                  # ⭐ Stack Observabilité Complète
│   ├── otel-collector/          # Configuration OpenTelemetry Collector
│   ├── prometheus/              # Configuration & alertes Prometheus
│   ├── grafana/                 # Provisioning des dashboards & sources
│   ├── loki/                    # Centralisation des logs
│   ├── promtail/                # Agent de collecte des logs
│   └── alertmanager/            # Gestion et routage des alertes
│
├── infra/                       # Infrastructure et déploiement
│   ├── docker/                  # Dockerfiles spécifiques aux services
│   └── dashboards/              # Définitions JSON des dashboards Grafana
│
├── scripts/                     # Scripts utilitaires (setup, seeding, etc.)
├── tests/                       # Tests unitaires et d'intégration
├── docs/                        # Documentation technique détaillée
├── .github/                     # Workflows CI/CD (GitHub Actions)
└── docker-compose.yml           # Orchestration des services en local
```

## Description des Composants Clés

### Apps
- **frontend**: Interface utilisateur moderne pour visualiser les statistiques et les prédictions.
- **l1-app-api**: Point d'entrée unique pour le frontend, gère l'authentification et l'agrégation des données.
- **l1-ml-api**: Service spécialisé dans l'exécution des modèles ML pour fournir des prédictions en temps réel.

### Monitoring
La stack d'observabilité suit les trois piliers (Traces, Métriques, Logs) :
- **Traces**: Collectées par OpenTelemetry depuis les APIs.
- **Métriques**: Exposées via `/metrics` et stockées dans Prometheus.
- **Logs**: Centralisés dans Loki via Promtail, corrélés aux traces via `trace_id`.

### Services Core
Le dossier `services/core` contient le socle technique réutilisable par tous les services internes, assurant une cohérence dans la configuration et l'observabilité de la plateforme.
