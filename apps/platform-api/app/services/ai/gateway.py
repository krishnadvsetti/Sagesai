import asyncio
import logging
import time

from app.observability.metrics import (
    AI_PROVIDER_FAILURES_TOTAL,
    AI_REQUEST_DURATION_SECONDS,
    AI_REQUESTS_TOTAL,
)
from app.services.ai.base import AIProvider
from app.services.ai.gemini import GeminiProvider
from app.services.guardrails import GuardrailService


logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when all configured AI providers fail."""


class AIGateway:
    def __init__(
        self,
        provider: AIProvider | None = None,
        fallback_providers: list[AIProvider] | None = None,
        timeout_seconds: float = 60.0,
        max_attempts: int = 3,
    ) -> None:
        self.primary_provider = provider or GeminiProvider()
        self.fallback_providers = fallback_providers or []
        self.guardrails = GuardrailService()
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        self.guardrails.enforce(prompt)

        providers = [
            self.primary_provider,
            *self.fallback_providers,
        ]

        errors: list[str] = []

        for provider in providers:
            provider_name = provider.__class__.__name__
            start_time = time.perf_counter()

            try:
                response = await self._generate_with_retry(
                    provider=provider,
                    prompt=prompt,
                    system_instruction=system_instruction,
                )

                AI_REQUESTS_TOTAL.labels(
                    provider=provider_name,
                    status="success",
                ).inc()

                return response

            except AIServiceError as exc:
                errors.append(
                    f"{provider_name}: {exc}"
                )

                AI_REQUESTS_TOTAL.labels(
                    provider=provider_name,
                    status="failure",
                ).inc()

                logger.error(
                    "AI provider %s exhausted all retries",
                    provider_name,
                )

            finally:
                duration = time.perf_counter() - start_time

                AI_REQUEST_DURATION_SECONDS.labels(
                    provider=provider_name,
                ).observe(duration)

        raise AIServiceError(
            "All AI providers failed. "
            + " | ".join(errors)
        )

    async def _generate_with_retry(
        self,
        provider: AIProvider,
        prompt: str,
        system_instruction: str | None,
    ) -> str:
        last_error: Exception | None = None
        provider_name = provider.__class__.__name__

        for attempt in range(
            1,
            self.max_attempts + 1,
        ):
            try:
                response = await asyncio.wait_for(
                    provider.generate(
                        prompt=prompt,
                        system_instruction=system_instruction,
                    ),
                    timeout=self.timeout_seconds,
                )

                if not response.strip():
                    raise RuntimeError(
                        "Provider returned an empty response"
                    )

                return response

            except Exception as exc:
                last_error = exc

                AI_PROVIDER_FAILURES_TOTAL.labels(
                    provider=provider_name,
                ).inc()

                logger.warning(
                    "%s failed on attempt %s/%s: %s",
                    provider_name,
                    attempt,
                    self.max_attempts,
                    exc,
                )

            if attempt < self.max_attempts:
                await asyncio.sleep(
                    2 ** (attempt - 1)
                )

        raise AIServiceError(
            f"Generation failed after "
            f"{self.max_attempts} attempts"
        ) from last_error