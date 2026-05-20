# Guide de Test du Système Distribué

Ce document répertorie les commandes pour valider que toute la chaîne (App API <-> ML API) fonctionne.

## 1. Vérification de la Santé (Healthchecks)

### App API
```bash
curl http://localhost:8002/health
```

### ML API
```bash
curl http://localhost:8001/health
```

## 2. Test d'Inférence (End-to-End)

Ce test simule un utilisateur demandant une prédiction pour un match. L'App API transmet la demande à la ML API.

```bash
curl -X POST "http://localhost:8002/predict/test?home_team=Marseille&away_team=Lyon" \
     -H "Content-Type: application/json"
```

**Réponse attendue :**
```json
{
  "match": "Marseille vs Lyon",
  "prediction_result": {
    "prediction": "A",
    "probabilities": { "A": 0.34, "D": 0.32, "H": 0.33 }
  }
}
```

## 3. Logs de Communication
Pour voir l'échange entre les services en temps réel :
```bash
docker compose logs -f app-api ml-api
```

## 4. Test Création Utilisateur (Persistance DB)
```bash
curl -X POST "http://localhost:8002/users" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```
