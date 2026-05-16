#!/bin/bash

set -e

echo "🚀 Starting App API Pipeline..."

# Fonction pour attendre que la DB soit prête
wait_for_db() {
  echo "⌛ Waiting for PostgreSQL to be ready on $POSTGRES_HOST:$POSTGRES_PORT..."
  while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 1
  done
  echo "✅ PostgreSQL is UP!"
}

# On définit les variables par défaut si non présentes
POSTGRES_HOST=${POSTGRES_HOST:-db-app}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

# Attente effective
wait_for_db

# 1. Run database migrations
echo "⚙️ Running migrations..."
cd /app/services/app-api
alembic upgrade head

# 2. Start Uvicorn
echo "✨ Starting Uvicorn..."
cd /app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
