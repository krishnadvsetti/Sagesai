from app.services.engineering.agents.base import BaseAgent


class ArchitectureAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "architecture_agent"

    @property
    def system_instruction(self) -> str:
        return (
            "You are a senior software architect. Produce practical architecture "
            "recommendations covering components, data flow, APIs, persistence, "
            "security, scalability, observability, and deployment."
        )