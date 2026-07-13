import httpx

from app.core.config.settings import settings


class AnomalyServiceError(Exception):
    pass


class AnomalyServiceClient:
    def __init__(self) -> None:
        self.base_url = settings.ANOMALY_SERVICE_URL.rstrip("/")

    async def predict(
        self,
        features: dict[str, float],
    ) -> dict[str, float | bool]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/predict",
                    json=features,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as exc:
            raise AnomalyServiceError(
                "Anomaly detection service is unavailable"
            ) from exc
