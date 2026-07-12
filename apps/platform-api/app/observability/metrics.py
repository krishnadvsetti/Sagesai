from prometheus_client import Counter, Histogram


HTTP_REQUESTS_TOTAL = Counter(
    "sagesai_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "sagesai_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

AI_REQUESTS_TOTAL = Counter(
    "sagesai_ai_requests_total",
    "Total AI generation requests",
    ["provider", "status"],
)

AI_REQUEST_DURATION_SECONDS = Histogram(
    "sagesai_ai_request_duration_seconds",
    "AI generation duration in seconds",
    ["provider"],
)

AI_PROVIDER_FAILURES_TOTAL = Counter(
    "sagesai_ai_provider_failures_total",
    "Total AI provider failures",
    ["provider"],
)

GUARDRAIL_BLOCKS_TOTAL = Counter(
    "sagesai_guardrail_blocks_total",
    "Total requests blocked by AI guardrails",
    ["risk_level"],
)

ML_INFERENCES_TOTAL = Counter(
    "sagesai_ml_inferences_total",
    "Total ML inference requests",
    ["model", "prediction", "status"],
)

ML_INFERENCE_DURATION_SECONDS = Histogram(
    "sagesai_ml_inference_duration_seconds",
    "ML inference duration in seconds",
    ["model"],
)

ML_PREDICTION_CONFIDENCE = Histogram(
    "sagesai_ml_prediction_confidence",
    "ML prediction confidence distribution",
    ["model", "prediction"],
)