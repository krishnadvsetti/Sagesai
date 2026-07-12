import json

from app.services.ai.gateway import AIGateway


class ToolSelector:
    def __init__(self, gateway: AIGateway) -> None:
        self.gateway = gateway

    async def select(self, task: str) -> dict:
        prompt = f"""
Choose the most appropriate tool for this engineering task.

Available tools:

1. repository_search
Use when the task requires information about source code,
files, configuration, classes, functions, or repository structure.

2. document_search
Use when the task requires information from uploaded enterprise
documents or the Sagesai knowledge base.

3. none
Use when no external context is required.

TASK:
{task}

Return ONLY valid JSON:

{{
  "tool": "repository_search",
  "query": "search query"
}}
"""

        response = await self.gateway.generate(
            prompt=prompt,
            system_instruction=(
                "You are a tool-routing system. "
                "Return valid JSON only."
            ),
        )

        cleaned = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(cleaned)

        allowed_tools = {
            "repository_search",
            "document_search",
            "none",
        }

        if result.get("tool") not in allowed_tools:
            raise ValueError("Invalid tool selected")

        return {
            "tool": result["tool"],
            "query": result.get("query", task),
        }