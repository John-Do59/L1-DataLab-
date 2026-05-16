FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copie sélective
COPY services/app-api/ services/app-api/

EXPOSE 8000

CMD ["uvicorn", "services.app-api.main:app", "--host", "0.0.0.0", "--port", "8000"]
