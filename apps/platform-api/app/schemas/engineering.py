from typing import Literal

from pydantic import BaseModel, Field


AgentType = Literal[
    "requirements",
    "architecture",
    "code_review",
]

ToolType = Literal[
    "repository_search",
    "document_search",
]


class AgentRequest(BaseModel):
    agent: AgentType
    task: str = Field(
        min_length=1,
        max_length=20_000,
    )


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


class ToolAgentRequest(BaseModel):
    agent: AgentType
    task: str = Field(
        min_length=1,
        max_length=20_000,
    )
    tool: ToolType
    tool_query: str = Field(
        min_length=1,
        max_length=2000,
    )


class ToolAgentResponse(BaseModel):
    agent: str
    tool: str
    tool_result: dict
    result: str


class AutoToolAgentRequest(BaseModel):
    agent: AgentType
    task: str = Field(
        min_length=1,
        max_length=20_000,
    )


class AutoToolAgentResponse(BaseModel):
    agent: str
    selected_tool: str
    tool_result: dict | None
    result: str