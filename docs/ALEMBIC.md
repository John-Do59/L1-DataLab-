# Alembic Database Migrations

**Alembic** est utilisé pour versionner le schéma de la base de données `l1_app`.

## Flux de travail
1. Modifier un modèle dans `app/models/models.py`.
2. Générer une migration : `alembic revision --autogenerate -m "description"`.
3. Appliquer : `alembic upgrade head`.

## Automatisation Docker
Dans le container `l1-app-api`, le script `start.sh` exécute automatiquement les migrations au démarrage :

```bash
# start.sh
alembic upgrade head
uvicorn app.main:app ...
```

## Commandes Essentielles

| Action | Commande |
| :--- | :--- |
| Initialiser | `alembic init alembic` |
| Créer migration | `alembic revision --autogenerate -m "msg"` |
| Appliquer | `alembic upgrade head` |
| Annuler (Rollback) | `alembic downgrade -1` |
| Voir historique | `alembic history --verbose` |

## Point Technique : Async vs Sync
Alembic utilise un moteur **synchrone** (`psycopg2-binary`) pour effectuer les modifications structurelles, tandis que l'application utilise un moteur **asynchrone** (`asyncpg`) pour les requêtes métier. Cette dualité est configurée dans `alembic/env.py`.
