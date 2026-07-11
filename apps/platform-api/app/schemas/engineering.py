from typing import Literal

from pydantic import BaseModel, Field


AgentType = Literal[
    "requirements",
    "architecture",
    "code_review",
]


class AgentRequest(BaseModel):
    agent: AgentType
    task: str = Field(min_length=1, max_length=20_000)


class AgentResponse(BaseModel):
    agent: str
    result: str


class ProjectAnalysisRequest(BaseModel):
    project_description: str = Field(
        min_length=10,
        max_length=20_000,
    )


class ProjectAnalysisResponse(BaseModel):
    requirements: str
    architecture: str