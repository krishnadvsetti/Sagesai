from app.services.ai.gateway import AIGateway
from app.services.engineering.agents.architecture import ArchitectureAgent
from app.services.engineering.agents.code_review import CodeReviewAgent
from app.services.engineering.agents.requirements import RequirementsAgent


class EngineeringOrchestrator:
    def __init__(self) -> None:
        gateway = AIGateway()

        self.agents = {
            "requirements": RequirementsAgent(gateway),
            "architecture": ArchitectureAgent(gateway),
            "code_review": CodeReviewAgent(gateway),
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