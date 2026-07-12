from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.guardrails import (
    GuardrailCheckRequest,
    GuardrailCheckResponse,
)
from app.services.guardrails import GuardrailService


router = APIRouter(
    prefix="/guardrails",
    tags=["AI Guardrails"],
)

guardrail_service = GuardrailService()


@router.post(
    "/check",
    response_model=GuardrailCheckResponse,
)
async def check_guardrails(
    payload: GuardrailCheckRequest,
    current_user: User = Depends(get_current_user),
) -> GuardrailCheckResponse:
    result = guardrail_service.check(payload.text)

    return GuardrailCheckResponse(
        allowed=result.allowed,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        detected_categories=result.detected_categories,
        reasons=result.reasons,
    )