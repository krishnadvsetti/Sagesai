from pydantic import BaseModel, Field


class RAGEvaluationRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    answer: str = Field(min_length=1, max_length=20_000)
    contexts: list[str] = Field(min_length=1, max_length=10)


class RAGEvaluationResponse(BaseModel):
    groundedness: float
    answer_relevance: float
    context_relevance: float
    overall_score: float
    evaluation: str

class RAGEvaluationCaseResult(BaseModel):
    name: str
    groundedness: float
    answer_relevance: float
    context_relevance: float
    overall_score: float
    evaluation: str
    latency_ms: float


class RAGEvaluationSuiteResponse(BaseModel):
    case_count: int
    average_groundedness: float
    average_answer_relevance: float
    average_context_relevance: float
    average_overall_score: float
    average_latency_ms: float
    benchmark_status: str
    passed: bool
    results: list[RAGEvaluationCaseResult]