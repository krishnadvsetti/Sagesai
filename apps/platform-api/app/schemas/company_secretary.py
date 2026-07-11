from pydantic import BaseModel, Field


class ComplianceAnalysisRequest(BaseModel):
    document_text: str = Field(min_length=20, max_length=30_000)


class ComplianceAnalysisResponse(BaseModel):
    analysis: str


class GovernanceQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=10)


class GovernanceQueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]