from app.services.engineering.agents.base import BaseAgent


class RequirementsAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "requirements_agent"

    @property
    def system_instruction(self) -> str:
        return (
            "You are a senior requirements engineer. Analyze software requests "
            "and produce clear functional requirements, non-functional "
            "requirements, assumptions, constraints, risks, and acceptance criteria."
        )