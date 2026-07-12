from app.services.ai.gateway import AIGateway
from app.services.engineering.agents.architecture import ArchitectureAgent
from app.services.engineering.agents.code_review import CodeReviewAgent
from app.services.engineering.agents.requirements import RequirementsAgent
from app.services.engineering.tool_selector import ToolSelector
from app.services.engineering.tools import ToolRegistry


class EngineeringOrchestrator:
    def __init__(self) -> None:
        self.gateway = AIGateway()
        self.tool_registry = ToolRegistry()
        self.tool_selector = ToolSelector(self.gateway)

        self.agents = {
            "requirements": RequirementsAgent(self.gateway),
            "architecture": ArchitectureAgent(self.gateway),
            "code_review": CodeReviewAgent(self.gateway),
        }

    async def run_agent(
        self,
        agent_name: str,
        task: str,
    ) -> dict[str, str]:
        agent = self.agents.get(agent_name)

        if agent is None:
            raise ValueError(f"Unknown agent: {agent_name}")

        result = await agent.run(task)

        return {
            "agent": agent.name,
            "result": result,
        }

    async def run_agent_with_tool(
        self,
        agent_name: str,
        task: str,
        tool_name: str,
        tool_query: str,
    ) -> dict:
        agent = self.agents.get(agent_name)

        if agent is None:
            raise ValueError(f"Unknown agent: {agent_name}")

        tool_result = await self.tool_registry.execute(
            tool_name,
            query=tool_query,
            max_results=5,
        )

        grounded_task = f"""
USER TASK:
{task}

TOOL USED:
{tool_name}

TOOL QUERY:
{tool_query}

TOOL RESULTS:
{tool_result}

Use the tool results as supporting context.
Do not invent repository or document facts that are not
supported by the provided tool results.
"""

        result = await agent.run(grounded_task)

        return {
            "agent": agent.name,
            "tool": tool_name,
            "tool_result": tool_result,
            "result": result,
        }

    async def run_agent_auto(
        self,
        agent_name: str,
        task: str,
    ) -> dict:
        agent = self.agents.get(agent_name)

        if agent is None:
            raise ValueError(f"Unknown agent: {agent_name}")

        selection = await self.tool_selector.select(task)

        tool_name = selection["tool"]
        tool_query = selection["query"]

        if tool_name == "none":
            result = await agent.run(task)

            return {
                "agent": agent.name,
                "selected_tool": "none",
                "tool_result": None,
                "result": result,
            }

        tool_result = await self.tool_registry.execute(
            tool_name,
            query=tool_query,
            max_results=5,
        )

        grounded_task = f"""
USER TASK:
{task}

AUTOMATICALLY SELECTED TOOL:
{tool_name}

TOOL QUERY:
{tool_query}

TOOL RESULTS:
{tool_result}

Use the tool results as supporting context.
Do not invent repository or document facts that are not
supported by the provided tool results.
"""

        result = await agent.run(grounded_task)

        return {
            "agent": agent.name,
            "selected_tool": tool_name,
            "tool_result": tool_result,
            "result": result,
        }

    async def analyze_project(
        self,
        project_description: str,
    ) -> dict[str, str]:
        requirements = await self.agents["requirements"].run(
            project_description
        )

        architecture = await self.agents["architecture"].run(
            f"""
Project:
{project_description}

Requirements analysis:
{requirements}

Design an appropriate production architecture.
"""
        )

        return {
            "requirements": requirements,
            "architecture": architecture,
        }