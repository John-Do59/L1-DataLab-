# Gestion des Dépendances - L1 DataLab

Pour garantir la propreté, la maintenabilité et la légèreté du projet, les dépendances sont divisées en plusieurs fichiers selon leur usage. Cela permet d'installer uniquement ce qui est nécessaire pour un service donné (ex: l'API de production n'a pas besoin de Scrapy ou de Pytest).

## Liste des fichiers de dépendances

### 1. `requirements.txt`
**Usage : Cœur de l'application (Production)**
Contient les bibliothèques indispensables au fonctionnement des APIs FastAPI, à la validation des données et à la connexion aux bases de données.
- *Inclus :* FastAPI, Pydantic, SQLAlchemy, Psycopg, Redis, Alembic.

### 2. `requirements-ml.txt`
**Usage : Machine Learning & Data Science**
Contient tout ce qui est nécessaire pour l'analyse de données, le feature engineering et l'entraînement/inférence des modèles ML.
- *Inclus :* Pandas, Numpy, Scikit-learn, XGBoost, Matplotlib.

### 3. `requirements-dev.txt`
**Usage : Développement, Tests & Scraping**
Outils utilisés uniquement pendant la phase de développement ou pour les tâches de collecte de données.
- *Inclus :* Pytest, Black, Ruff, Scrapy, Playwright.

### 4. `requirements-monitoring.txt`
**Usage : Observabilité & Monitoring**
Bibliothèques pour l'instrumentation OpenTelemetry et l'exposition des métriques Prometheus.
- *Inclus :* OpenTelemetry SDK, Prometheus Client, Loguru.

---

## Instructions d'installation

Il est fortement recommandé d'utiliser un environnement virtuel (`.venv`).

### Tout installer (Environnement complet de Dev)
```bash
pip install -r requirements.txt -r requirements-ml.txt -r requirements-dev.txt -r requirements-monitoring.txt
```

### Installer uniquement pour la production
```bash
pip install -r requirements.txt -r requirements-monitoring.txt
```

### Installer uniquement pour le ML / Data Science
```bash
pip install -r requirements.txt -r requirements-ml.txt
```

---

## Bonnes Pratiques
- **Versionnement :** Ces fichiers doivent être versionnés dans Git.
- **Ajout de librairie :** Si vous ajoutez une librairie, choisissez le fichier le plus pertinent pour éviter de polluer les autres environnements.
- **Isolation :** Ne jamais versionner le dossier `.venv/` (déjà exclu dans le `.gitignore`).
