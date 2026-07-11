from google import genai
from google.genai import types

from app.core.config.settings import settings
from app.services.ai.base import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        response = await self.client.aio.models.generate_content(
            model=settings.AI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=settings.AI_TEMPERATURE,
                max_output_tokens=settings.AI_MAX_OUTPUT_TOKENS,
            ),
        )

        return response.text or ""