from typing import Any

from app.services.engineering.tools.base import BaseTool
from app.services.engineering.tools.document_search import (
    DocumentSearchTool,
)
from app.services.engineering.tools.repository_search import (
    RepositorySearchTool,
)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

        self.register(RepositorySearchTool())
        self.register(DocumentSearchTool())

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")

        return self._tools[name]

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self._tools.values()
        ]

    async def execute(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> dict:
        tool = self.get(tool_name)
        return await tool.execute(**kwargs)