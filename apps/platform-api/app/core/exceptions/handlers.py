import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.observability.request_context import (
    correlation_id_context,
    request_id_context,
)
from app.services.ai.gateway import AIServiceError


logger = logging.getLogger("sagesai.exceptions")


def _error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {
        "code": error_code,
        "message": message,
        "request_id": request_id_context.get(),
        "correlation_id": correlation_id_context.get(),
        "timestamp": datetime.now(UTC).isoformat(),
    }

    if details is not None:
        error["details"] = details

    return JSONResponse(
        status_code=status_code,
        content={"error": error},
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}",
        message=(
            exc.detail
            if isinstance(exc.detail, str)
            else "HTTP request failed"
        ),
        details=(
            exc.detail
            if not isinstance(exc.detail, str)
            else None
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details=exc.errors(),
    )


async def ai_service_exception_handler(
    request: Request,
    exc: AIServiceError,
) -> JSONResponse:
    logger.error(
        "AI service unavailable",
        extra={
            "request_id": request_id_context.get(),
            "correlation_id": correlation_id_context.get(),
        },
    )

    return _error_response(
        status_code=503,
        error_code="AI_SERVICE_UNAVAILABLE",
        message="AI service is temporarily unavailable",
    )


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception(
        "Database operation failed",
        extra={
            "request_id": request_id_context.get(),
            "correlation_id": correlation_id_context.get(),
        },
    )

    return _error_response(
        status_code=503,
        error_code="DATABASE_UNAVAILABLE",
        message="Database service is temporarily unavailable",
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled application exception",
        extra={
            "request_id": request_id_context.get(),
            "correlation_id": correlation_id_context.get(),
        },
    )

    return _error_response(
        status_code=500,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal error occurred",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

    app.add_exception_handler(
        AIServiceError,
        ai_service_exception_handler,
    )

    app.add_exception_handler(
        SQLAlchemyError,
        database_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )