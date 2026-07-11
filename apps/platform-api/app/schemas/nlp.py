from pydantic import BaseModel, Field


class EntityExtractionRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=10_000,
    )


class ExtractedEntity(BaseModel):
    text: str
    entity_type: str
    confidence: float
    start: int
    end: int


class EntityExtractionResponse(BaseModel):
    entities: list[ExtractedEntity]
    entity_count: int