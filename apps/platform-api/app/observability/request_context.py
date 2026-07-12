from contextvars import ContextVar


request_id_context: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)

correlation_id_context: ContextVar[str | None] = ContextVar(
    "correlation_id",
    default=None,
)