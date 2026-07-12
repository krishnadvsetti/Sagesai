from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs: Any) -> dict:
        """Execute the tool and return a structured result."""
        raise NotImplementedError