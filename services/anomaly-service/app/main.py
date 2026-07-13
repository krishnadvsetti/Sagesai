from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.inference import AnomalyDetector


detector: AnomalyDetector | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global detector
    detector = AnomalyDetector()
    yield
    detector = None


app = FastAPI(
    title="Sagesai Anomaly Detection Service",
    version="0.1.0",
    lifespan=lifespan,
)


class AnomalyDetectionRequest(BaseModel):
    failed_logins: float = Field(ge=0)
    login_hour: float = Field(ge=0, le=23)
    request_rate: float = Field(ge=0)
    unique_ips: float = Field(ge=0)
    privilege_actions: float = Field(ge=0)
    data_transfer_mb: float = Field(ge=0)


class AnomalyDetectionResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    threshold: float


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "anomaly-service",
    }


@app.post(
    "/predict",
    response_model=AnomalyDetectionResponse,
)
async def predict(
    payload: AnomalyDetectionRequest,
) -> AnomalyDetectionResponse:
    if detector is None:
        raise RuntimeError("Anomaly detector is not initialized")

    result = detector.predict(payload.model_dump())

    return AnomalyDetectionResponse(**result)
