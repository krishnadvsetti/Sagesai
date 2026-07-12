import time
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config.settings import settings
from app.database.session import engine


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Service health check",
)
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Service liveness check",
)
async def liveness_check() -> dict:
    return {
        "status": "alive",
        "service": settings.APP_NAME,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Service readiness check",
)
async def readiness_check() -> dict:
    started_at = time.perf_counter()

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        database_latency_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        return {
            "status": "ready",
            "service": settings.APP_NAME,
            "checks": {
                "database": {
                    "status": "up",
                    "latency_ms": database_latency_ms,
                }
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "service": settings.APP_NAME,
                "checks": {
                    "database": {
                        "status": "down",
                    }
                },
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ) from exc