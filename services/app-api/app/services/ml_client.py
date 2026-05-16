import httpx
import os
from fastapi import HTTPException

class MLClient:
    def __init__(self):
        self.ml_api_url = os.getenv("ML_API_URL", "http://ml-api:8000")

    async def get_prediction(self, features: dict):
        """
        Appelle l'API ML pour obtenir une prédiction.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.ml_api_url}/predict",
                    json=features
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"ML API error: {e.response.text}"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"ML API unreachable: {str(e)}"
                )

ml_client = MLClient()
