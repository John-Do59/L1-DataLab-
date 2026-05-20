FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copie le CONTENU de services/app-api à la racine /app
COPY services/app-api/ .

EXPOSE 8000

# On s'assure que le script est exécutable
RUN chmod +x start.sh

CMD ["./start.sh"]
