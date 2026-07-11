from abc import ABC, abstractmethod

from app.services.ai.gateway import AIGateway


class BaseAgent(ABC):
    def __init__(self, gateway: AIGateway) -> None:
        self.gateway = gateway

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def system_instruction(self) -> str:
        raise NotImplementedError

    async def run(self, task: str) -> str:
        return await self.gateway.generate(
            prompt=task,
            system_instruction=self.system_instruction,
        )