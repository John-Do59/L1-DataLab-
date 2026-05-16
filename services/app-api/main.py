from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI(title="Ligue 1 App API", version="1.0.0")

ML_API_URL = os.getenv("ML_API_URL", "http://localhost:8001")

@app.get("/")
def read_root():
    return {"message": "Welcome to Ligue 1 App API"}

@app.get("/matches")
def get_matches():
    # Ici on interrogerait db-app
    return {"matches": []}

@app.post("/predict/{match_id}")
async def get_prediction(match_id: str, features: dict):
    """Proxy vers l'API ML"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{ML_API_URL}/predict", json=features)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=500, detail=f"ML API Error: {str(exc)}")

@app.get("/health")
def health():
    return {"status": "healthy"}
