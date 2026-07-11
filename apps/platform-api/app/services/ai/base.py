from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        raise NotImplementedError