# 🏗️ L1 DataLab — Phase 2 : Data Modeling & ETL

> **Branche** : `feature/data-modeling-etl`  
> **Statut** : ✅ Schéma + Scripts ETL créés | ⏳ PostgreSQL à démarrer  
> **Objectif** : Transformer le Data Lake (CSV/JSON) en un Data Warehouse structuré prêt pour le Machine Learning.

---

## 📌 Pourquoi cette phase ?

Après la phase d'acquisition (scraping + Kaggle), nous avions des **données éparpillées** dans des formats hétérogènes :
- `data/raw/*.json` (API Ligue 1)
- `data/historical/*.csv` (Kaggle)
- `data/betting/*.csv` (Football-Data.co.uk)
- `data/transfermarkt/*.csv`
- `data/fc24/*.csv`

**Le problème fondamental** : chaque source nomme les clubs différemment.
| Source | Nom PSG |
|---|---|
| API Ligue 1 | `Paris Saint-Germain` |
| Kaggle | `Paris SG` |
| Football-Data.co.uk | `Paris SG` |
| FC24 | `Paris Saint Germain` |
| Transfermarkt | `Paris SG` |

👉 La Phase 2 résout ce problème via un **Data Warehouse PostgreSQL** avec une table de mapping cross-source.

---

## 🗄️ Ce qui a été créé

### 1. Schéma PostgreSQL (`db/init_db.sql`)

8 tables construites dans cet ordre logique :

```
teams               ← Table pivot (source de vérité des clubs)
entity_mapping      ← Clé du projet : fait correspondre tous les noms
matches             ← Historique complet (Kaggle 1999-2019 + Live API)
players             ← Joueurs L1 (males uniquement)
betting_odds        ← Cotes bookmakers (feature ML cruciale)
fc24_attributes     ← Stats techniques joueurs (EA FC24)
transfermarkt_values← Valeurs marchandes
team_stats_snapshot ← Snapshots pré-calculés (feature engineering)
```

#### Diagramme des relations

```
entity_mapping ──→ teams ←── matches
                             ↑     ↑
                       betting_odds  |
                                     |
                   players ──────────┘
                     ↑         ↑
             fc24_attributes   transfermarkt_values
```

### 2. Seed Minimal (`db/seed_minimal.sql`)

Avant tout ETL massif, un seed de **validation** :
- 5 équipes (PSG, OM, OL, RC Lens, Reims)
- 10 matchs historiques
- 2 joueurs de test

Permet de vérifier que le schéma est cohérent.

### 3. Scripts ETL (ordre strict)

| # | Script | Source → Cible | Dépendances |
|---|--------|---------------|-------------|
| 1 | `etl_step1_teams.py` | `data/raw/l1_clubs/*.json` → `teams` + `entity_mapping` | aucune |
| 2 | `etl_step2_kaggle.py` | `data/historical/*.csv` → `matches` | Step 1 |
| 3 | `etl_step3_api.py` | `data/raw/l1_matches/*.json` → `matches` | Step 1 |
| 4 | `etl_step4_betting.py` | `data/betting/*.csv` → `betting_odds` | Step 1 + 3 |
| 5 | `etl_step5_players.py` | `data/fc24/male_players.csv` → `players` + `fc24_attributes` | Step 1 |
| 6 | `etl_step6_values.py` | `data/transfermarkt/*.csv` → `transfermarkt_values` | Step 5 |

### 4. Feature Engineering (`ml/features/create_ml_dataset.py`)

Calcule automatiquement depuis la DB :
- **Rolling form** : Points sur les 5 derniers matchs
- **Offensive / Defensive strength** : Moyenne de buts sur 5 matchs
- **Squad strength** : Moyenne FC24 overall par équipe
- **Squad value** : Valeur totale Transfermarkt par équipe
- **Betting probabilities** : Probabilités implicites des cotes (1/cote)

Produit deux fichiers CSV prêts pour sklearn :
- `ml/features/ml_dataset.csv` — Historique complet
- `ml/features/ml_dataset_with_odds.csv` — Avec cotes (saison récente)

---

## 🚀 Phase 3 : Démarrer PostgreSQL et lancer l'ETL

### Prérequis

- Docker Desktop installé et lancé
- Variables d'environnement configurées

### Étape 1 — Créer le fichier `.env` à la racine

```bash
# .env
DATABASE_URL=postgresql://l1user:l1password@localhost:5432/l1_datalab
POSTGRES_USER=l1user
POSTGRES_PASSWORD=l1password
POSTGRES_DB=l1_datalab
```

### Étape 2 — Démarrer PostgreSQL avec Docker

```bash
# Démarrer uniquement le service PostgreSQL
docker compose up -d postgres
```

> Si tu n'as pas encore de `docker-compose.yml`, voir la section suivante.

### Étape 3 — Initialiser le schéma

```bash
# Se connecter à la base et créer les tables
docker exec -i l1datalab-postgres psql -U l1user -d l1_datalab < db/init_db.sql

# Vérifier que les tables ont été créées
docker exec -it l1datalab-postgres psql -U l1user -d l1_datalab -c "\dt"
```

### Étape 4 — Seed Minimal (validation)

```bash
# Insérer les données de test
docker exec -i l1datalab-postgres psql -U l1user -d l1_datalab < db/seed_minimal.sql

# Vérifier
docker exec -it l1datalab-postgres psql -U l1user -d l1_datalab \
  -c "SELECT count(*) FROM teams; SELECT count(*) FROM matches;"
```

### Étape 5 — S'assurer d'avoir les données brutes

```bash
# Si les données ne sont pas encore téléchargées
export PYTHONPATH=$PYTHONPATH:/Users/amaury/Library/Python/3.9/lib/python/site-packages

python3 scripts/download_historical_data.py   # Kaggle (Historique + Transfermarkt + FC24)
python3 scripts/download_betting_odds.py       # Football-Data.co.uk
scrapy crawl l1_clubs      # API Ligue 1 (depuis services/scraper/)
scrapy crawl l1_matches
scrapy crawl l1_standings
```

### Étape 6 — Lancer le pipeline ETL complet

```bash
# Option A : Tout en une commande (recommandé)
export DATABASE_URL=postgresql://l1user:l1password@localhost:5432/l1_datalab
python3 scripts/run_etl.py

# Option B : Pas à pas (pour debug)
python3 scripts/etl_step1_teams.py    # Normalisation équipes
python3 scripts/etl_step2_kaggle.py   # Historique 1999-2019
python3 scripts/etl_step3_api.py      # Saison actuelle
python3 scripts/etl_step4_betting.py  # Cotes bookmakers
python3 scripts/etl_step5_players.py  # Joueurs FC24 (males L1)
python3 scripts/etl_step6_values.py   # Valeurs Transfermarkt
```

### Étape 7 — Générer le Dataset ML

```bash
python3 ml/features/create_ml_dataset.py
# Fichiers générés dans ml/features/
```

---

## 📋 Configuration `docker-compose.yml` (PostgreSQL minimal)

Si pas encore configuré, ajouter ce service dans `docker-compose.yml` :

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: l1datalab-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-l1user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-l1password}
      POSTGRES_DB: ${POSTGRES_DB:-l1_datalab}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-l1user}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

---

## ✅ Checklist de validation post-ETL

Après avoir lancé tous les scripts, vérifier en SQL :

```sql
-- Nombre d'équipes mappées
SELECT count(*) FROM teams;                          -- attendu : ~18-40

-- Couverture du mapping cross-source
SELECT source, count(*) FROM entity_mapping
GROUP BY source ORDER BY source;

-- Nombre de matchs par source
SELECT source, count(*) FROM matches GROUP BY source;

-- Matchs avec cotes (pour le ML)
SELECT count(*) FROM matches m
JOIN betting_odds bo ON bo.match_id = m.id;

-- Vérifier les joueurs FC24 chargés
SELECT count(*) FROM fc24_attributes;

-- Dataset ML : taille et distribution des labels
-- (après create_ml_dataset.py)
SELECT result, count(*), round(count(*) * 100.0 / sum(count(*)) over(), 1) AS pct
FROM matches WHERE result IS NOT NULL
GROUP BY result;
-- Attendu : H ~45%, D ~25%, A ~30%
```

---

## ⚠️ Points d'attention importants

> [!IMPORTANT]
> **Le répertoire `data/` n'est PAS pushé sur GitHub** (`.gitignore`). Chaque développeur doit relancer les scripts de téléchargement.

> [!WARNING]
> **Ordre ETL strict** : Ne jamais lancer Step 2 avant Step 1. `run_etl.py` gère ça automatiquement.

> [!TIP]
> Le matching par nom d'équipe est le point le plus fragile. Si un club n'est pas résolu, vérifier le dictionnaire `TEAM_NAME_MAPPING` dans `etl_step1_teams.py` et ajouter le mapping manquant.

---

## 🧠 Ce que tu construis ici

```
❌ Avant Phase 2 :
   CSV/JSON éparpillés → pas de requêtes SQL → pas de ML propre

✅ Après Phase 2 :
   Sports Data Warehouse PostgreSQL → Features ML calculées automatiquement
   → Dataset H/D/A prêt pour scikit-learn
```

**Ce niveau d'architecture (ETL + Data Warehouse + Feature Engineering) est exactement ce qui est valorisé dans un projet RNCP niveau 5/6.**
