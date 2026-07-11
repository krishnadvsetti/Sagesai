from app.services.ai.base import AIProvider
from app.services.ai.gemini import GeminiProvider


class AIGateway:
    def __init__(self, provider: AIProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        return await self.provider.generate(
            prompt=prompt,
            system_instruction=system_instruction,
        )