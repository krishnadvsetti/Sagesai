from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.evaluation import (
    RAGEvaluationRequest,
    RAGEvaluationResponse,
)
from app.services.evaluation.rag_evaluator import RAGEvaluator
from app.schemas.evaluation import (
    RAGEvaluationSuiteResponse,
)
from app.services.evaluation.runner import RAGEvaluationRunner


router = APIRouter(
    prefix="/evaluation",
    tags=["LLM & RAG Evaluation"],
)

evaluator: RAGEvaluator | None = None


def get_evaluator() -> RAGEvaluator:
    global evaluator
    if evaluator is None:
        evaluator = RAGEvaluator()
    return evaluator


@router.post(
    "/rag",
    response_model=RAGEvaluationResponse,
)
async def evaluate_rag_response(
    payload: RAGEvaluationRequest,
    current_user: User = Depends(get_current_user),
) -> RAGEvaluationResponse:
    try:
        result = await get_evaluator().evaluate(
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

runner: RAGEvaluationRunner | None = None


def get_runner() -> RAGEvaluationRunner:
    global runner
    if runner is None:
        runner = RAGEvaluationRunner()
    return runner


@router.post(
    "/rag/suite",
    response_model=RAGEvaluationSuiteResponse,
)
async def run_rag_evaluation_suite(
    current_user: User = Depends(get_current_user),
) -> RAGEvaluationSuiteResponse:
    result = await get_runner().run()

    return RAGEvaluationSuiteResponse(**result)