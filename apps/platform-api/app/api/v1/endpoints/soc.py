from fastapi import APIRouter, Depends

from app.api.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.schemas.soc import (
    SecurityAnalysisResponse,
    SecurityEventRequest,
)
from app.services.soc.service import SOCAnalystService

router = APIRouter(
    prefix="/soc",
    tags=["SOC Cybersecurity Analyst"],
)


@router.post(
    "/analyze-event",
    response_model=SecurityAnalysisResponse,
)
async def analyze_security_event(
    payload: SecurityEventRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.SECURITY_ANALYST,
        )
    ),
) -> SecurityAnalysisResponse:
    service = SOCAnalystService()

    result = await service.analyze(payload)

    return SecurityAnalysisResponse(**result)