from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class SearchResult(BaseModel):
    content: str
    metadata: dict
    score: float
    rerank_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class SourceCitation(BaseModel):
    citation_id: int
    document_id: str
    filename: str
    chunk_index: int
    score: float
    rerank_score: float


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SearchResult]
    citations: list[SourceCitation]