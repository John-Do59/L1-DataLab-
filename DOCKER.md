# 🐳 Guide Infrastructure Docker - L1 DataLab

Ce document détaille l'implémentation, l'optimisation et la gestion de l'infrastructure conteneurisée.

## 🏗️ Plan d'implémentation
L'architecture repose sur une orchestration multi-services (Microservices) :
- **2 Bases de données PostgreSQL** : Isolation totale entre les données de Machine Learning (`l1_ml`) et les données métier (`l1_app`).
- **2 APIs FastAPI** : 
    - `ml-api` : Service d'inférence haute performance chargeant le modèle XGBoost v1.
    - `app-api` : Gateway applicative gérant la logique métier et le proxying vers l'IA.

## 🚀 Optimisation des Images
Une attention particulière a été portée sur le poids des images pour garantir des déploiements rapides.

| État | Taille de l'image | Action menée |
| :--- | :--- | :--- |
| **Initial** | ~3.65 Go | Copie complète du root (incluant datasets lourds et venv). |
| **Final** | **1.24 Go** | Utilisation de `.dockerignore`, `requirements-api.txt` minimal et copies sélectives. |

**Gain total : 66% de réduction (soit ~4.8 Go d'espace économisé).**

---

## 🛠️ Commandes Utiles

### Gestion du cycle de vie
- **Démarrage complet** : `docker compose up -d`
- **Reconstruction après modification** : `docker compose up -d --build`
- **Arrêt et nettoyage** : `docker compose down`

### Diagnostics & Logs
- **Voir les logs en temps réel** : `docker compose logs -f`
- **Vérifier la santé des services** : 
    - ML API : `curl http://localhost:8001/health`
    - App API : `curl http://localhost:8002/health`
- **Tester une prédiction via l'App API** :
```bash
curl -X POST http://localhost:8002/predict/match_123 -H "Content-Type: application/json" -d '{
  "home_elo": 1600.0, "away_elo": 1450.0, "elo_diff": 150.0,
  "home_form_5": 0.8, "away_form_5": 0.4, "home_avg_overall": 78.0,
  "away_avg_overall": 72.0, "home_squad_value": 250.5, "away_squad_value": 80.2,
  "odds_prob_home": 0.6, "odds_prob_draw": 0.25, "odds_prob_away": 0.15
}'
```

### Maintenance Database
- **Accéder à la DB ML** : `docker exec -it l1-db-ml psql -U l1user -d l1_ml`
- **Accéder à la DB App** : `docker exec -it l1-db-app psql -U l1user -d l1_app`

---

## 🔒 Sécurité & Best Practices
- **Variables d'environnement** : Toutes les informations sensibles (mots de passe, URLs) sont injectées via le fichier `.env`.
- **Persistance** : Les volumes Docker assurent que les données ne sont pas perdues lors d'un redémarrage des containers.
- **Réseau isolé** : Les services communiquent via un réseau interne Docker, protégeant l'accès direct aux bases de données depuis l'extérieur.
