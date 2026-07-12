from pydantic import BaseModel, Field


class GuardrailCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)


class GuardrailCheckResponse(BaseModel):
    allowed: bool
    risk_score: float
    risk_level: str
    detected_categories: list[str]
    reasons: list[str]