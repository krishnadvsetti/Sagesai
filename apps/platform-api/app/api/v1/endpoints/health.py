from datetime import UTC, datetime

from fastapi import APIRouter, status

from app.core.config.settings import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Service health check",
)
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Service readiness check",
)
async def readiness_check() -> dict[str, str]:
    return {
        "status": "ready",
        "service": settings.APP_NAME,
    }
