from fastapi import APIRouter, Depends

from app.api.dependencies.auth import require_roles
from app.services.anomaly import AnomalyServiceClient
from app.models.user import User, UserRole
from app.schemas.soc import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    SecurityAnalysisResponse,
    SecurityEventRequest,
)
from app.services.soc.service import SOCAnalystService


router = APIRouter(
    prefix="/soc",
    tags=["SOC Cybersecurity Analyst"],
)

anomaly_client = AnomalyServiceClient()


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


@router.post(
    "/detect-anomaly",
    response_model=AnomalyDetectionResponse,
)
async def detect_anomaly(
    payload: AnomalyDetectionRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.SECURITY_ANALYST,
        )
    ),
) -> AnomalyDetectionResponse:
    result = await anomaly_client.predict(payload.model_dump())

    return AnomalyDetectionResponse(**result)