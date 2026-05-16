#!/bin/bash

set -e

echo "🚀 Starting App API Pipeline (Flat Structure)..."

# Fonction pour attendre que la DB soit prête
wait_for_db() {
  echo "⌛ Waiting for PostgreSQL to be ready on $POSTGRES_HOST:$POSTGRES_PORT..."
  while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 1
  done
  echo "✅ PostgreSQL is UP!"
}

POSTGRES_HOST=${POSTGRES_HOST:-db-app}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

wait_for_db

# 1. Run database migrations
echo "⚙️ Running migrations..."
alembic upgrade head

# 2. Start Uvicorn
echo "✨ Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
