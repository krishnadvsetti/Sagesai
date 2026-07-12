import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.request_context import (
    correlation_id_context,
    request_id_context,
)


logger = logging.getLogger("sagesai.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        correlation_id = request.headers.get(
            "X-Correlation-ID",
            request_id,
        )

        request_id_token = request_id_context.set(request_id)
        correlation_id_token = correlation_id_context.set(
            correlation_id
        )

        started_at = time.perf_counter()

        try:
            response = await call_next(request)

            duration_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id

            logger.info(
                "HTTP request completed",
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )

            return response

        except Exception:
            duration_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

            logger.exception(
                "HTTP request failed",
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                },
            )

            raise

        finally:
            request_id_context.reset(request_id_token)
            correlation_id_context.reset(
                correlation_id_token
            )