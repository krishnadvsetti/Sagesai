from typing import Literal

from pydantic import BaseModel, Field


class SecurityEventRequest(BaseModel):
    event_type: str = Field(min_length=2, max_length=200)
    source_ip: str | None = None
    destination_ip: str | None = None
    username: str | None = None
    description: str = Field(min_length=10, max_length=10_000)


class SecurityAnalysisResponse(BaseModel):
    severity: Literal["low", "medium", "high", "critical"]
    risk_score: int
    analysis: str

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