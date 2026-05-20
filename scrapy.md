# Stratégie de Collecte de Données - Scrapy & ma-api.ligue1.fr

Ce document détaille l'approche technique pour l'ingestion des données de la Ligue 1, en utilisant les endpoints JSON de l'API officielle.

## 1. Vision Technique
L'objectif est d'utiliser `services/scraper/` comme un module d'ingestion robuste capable de consommer les données structurées fournies par `ma-api.ligue1.fr`. 

### 2. Stratégie Multi-Sources
Le projet utilise désormais une approche hybride pour maximiser la profondeur des données :

- **Source API Officielle (`ma-api.ligue1.fr`)** :
    - Données en temps réel (matchs de la semaine, classements live).
    - Métadonnées riches (logos haute résolution, couleurs de clubs, stades).
- **Source Historique (Kaggle)** :
    - Dataset : `brunoo/ligue-1-results-1999-to-2019`.
    - Fournit plus de 20 ans d'historique de résultats pour l'entraînement des modèles ML.
    - Automatisé via le script `scripts/download_historical_data.py`.

### Pourquoi cette approche ?
- **Données JSON natives** : Pas besoin de parsing HTML complexe.
- **Précision** : Accès direct aux ID officiels (matchs, clubs, compétitions).
- **Performance** : Les spiders Scrapy peuvent récupérer les données de manière asynchrone et efficace.

## 2. Architecture du Scraper

Le projet Scrapy est situé dans `services/scraper/` et suit la structure standard :

```text
services/
  scraper/
    scraper/
      spiders/
        matches.py          # Calendriers et scores
        standings.py        # Classements généraux
        clubs.py            # Infos clubs et stades
        settings_spider.py  # Métadonnées championnat
        articles.py         # Flux d'actualités (RAG)
      items.py              # Schémas de données Pydantic-like
      pipelines.py          # Export JSON / Insertion Postgres
      settings.py           # Config (Headers, Middlewares)
      common.py             # Headers communs
```

## 3. Configuration des Requêtes (Headers)

Pour garantir le succès des requêtes, nous utilisons les headers identifiés sur la plateforme officielle :

```python
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://ligue1.com",
    "Referer": "https://ligue1.com/",
    "application": "ligue1",
    "client-language": "fr-FR",
    "client-version": "3.8.0",
    "platform": "web",
}
```

## 4. Plan d'Implémentation des Spiders

### 4.1 Matches (`l1_matches`)
- **Endpoint** : `https://ma-api.ligue1.fr/championships-daily-calendars/matches`
- **Rôle** : Récupérer les résultats passés pour le ML et les matchs à venir pour les prédictions.

### 4.2 Standings (`l1_standings`)
- **Endpoint** : `https://ma-api.ligue1.fr/championship-standings/1/general`
- **Rôle** : Fournir l'état actuel du classement pour les insights et le frontend.

### 4.3 Clubs (`l1_clubs`)
- **Endpoint** : `https://ma-api.ligue1.fr/championship-clubs`
- **Rôle** : Référentiel des équipes (noms, logos, villes, stades).

### 4.4 Articles (`l1_articles`)
- **Endpoint** : `https://ma-api.ligue1.fr/articles`
- **Rôle** : Alimenter la base vectorielle du RAG pour fournir du contexte textuel aux analyses.

## 5. Pipeline de Traitement des Données

1. **Extraction** : Scrapy récupère le JSON brut.
2. **Validation** : Passage par les `items.py` pour garantir l'intégrité.
3. **Stockage Temporaire** : Écriture dans `data/raw/` au format JSON.
4. **Insertion DB** : Pipeline SQLAlchemy pour charger les données dans :
   - `l1_ml` : Pour l'entraînement du modèle.
   - `l1_app` : Pour l'exposition via l'API produit.

## 6. Positionnement et Éthique
Dans le cadre de ce projet (Portfolio/RNCP), la démarche est présentée comme une **collecte automatisée à partir des APIs officielles**. L'accent est mis sur la maîtrise technique (ingestion d'APIs, nettoyage, stockage relationnel) plutôt que sur le reverse-engineering des endpoints.

---

## 🚀 Prochaines étapes
1. Initialiser le projet Scrapy dans `services/scraper/`.
2. Implémenter le premier spider (`l1_clubs`) pour avoir un référentiel solide.
3. Configurer le pipeline d'insertion asynchrone dans PostgreSQL.
