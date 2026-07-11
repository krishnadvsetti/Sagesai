from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.evaluation import (
    RAGEvaluationRequest,
    RAGEvaluationResponse,
)
from app.services.evaluation.rag_evaluator import RAGEvaluator
from app.schemas.evaluation import (
    RAGEvaluationRequest,
    RAGEvaluationResponse,
    RAGEvaluationSuiteResponse,
)
from app.services.evaluation.runner import RAGEvaluationRunner


router = APIRouter(
    prefix="/evaluation",
    tags=["LLM & RAG Evaluation"],
)

evaluator = RAGEvaluator()


@router.post(
    "/rag",
    response_model=RAGEvaluationResponse,
)
async def evaluate_rag_response(
    payload: RAGEvaluationRequest,
    current_user: User = Depends(get_current_user),
) -> RAGEvaluationResponse:
    try:
        result = await evaluator.evaluate(
            question=payload.question,
            answer=payload.answer,
            contexts=payload.contexts,
        )

        return RAGEvaluationResponse(**result)

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The evaluation model returned an invalid response.",
        ) from exc

runner = RAGEvaluationRunner()


@router.post(
    "/rag/suite",
    response_model=RAGEvaluationSuiteResponse,
)
async def run_rag_evaluation_suite(
    current_user: User = Depends(get_current_user),
) -> RAGEvaluationSuiteResponse:
    result = await runner.run()

    return RAGEvaluationSuiteResponse(**result)