#!/bin/bash
set -e

echo "1. Inscription..."
curl -s -X POST "http://localhost:8002/users" \
     -H "Content-Type: application/json" \
     -d '{"username": "johndoe", "email": "john@example.com", "password": "securepwd"}' > /dev/null || true

echo "2. Connexion..."
TOKEN=$(curl -s -X POST "http://localhost:8002/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=johndoe&password=securepwd" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token reçu: $TOKEN"

echo "3. Prédiction Dynamique (PSG vs OM)..."
curl -s -X POST "http://localhost:8002/predict?home_team_name=Paris%20Saint-Germain&away_team_name=Marseille" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" | jq .
