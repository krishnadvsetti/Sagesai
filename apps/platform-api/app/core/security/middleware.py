from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_request_size: int,
    ) -> None:
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                if int(content_length) > self.max_request_size:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "code": "REQUEST_TOO_LARGE",
                                "message": (
                                    "Request body exceeds the allowed size."
                                ),
                            }
                        },
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "INVALID_CONTENT_LENGTH",
                            "message": "Invalid Content-Length header.",
                        }
                    },
                )

        return await call_next(request)