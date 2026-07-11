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