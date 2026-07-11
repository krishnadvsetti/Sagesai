from app.services.engineering.agents.base import BaseAgent


class CodeReviewAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "code_review_agent"

    @property
    def system_instruction(self) -> str:
        return (
            "You are a senior software engineer performing a production code review. "
            "Identify correctness issues, security risks, maintainability problems, "
            "performance concerns, and concrete improvements. Do not invent issues."
        )