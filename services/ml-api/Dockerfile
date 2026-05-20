FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy all necessary workspace modules for ML pipeline orchestration
COPY ml/ /app/ml/
COPY scripts/ /app/scripts/
COPY services/ml-api/ /app/services/ml-api/

EXPOSE 8000

# Run from project root to ensure clean package import resolution
CMD ["uvicorn", "services.ml-api.main:app", "--host", "0.0.0.0", "--port", "8000"]
