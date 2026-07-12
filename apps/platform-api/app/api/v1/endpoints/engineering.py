from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.engineering import (
    AgentRequest,
    AgentResponse,
    AutoToolAgentRequest,
    AutoToolAgentResponse,
    ProjectAnalysisRequest,
    ProjectAnalysisResponse,
    ToolAgentRequest,
    ToolAgentResponse,
)
from app.services.engineering.orchestrator import EngineeringOrchestrator


router = APIRouter(
    prefix="/engineering",
    tags=["Software Engineering Assistant"],
)


@router.post(
    "/agent",
    response_model=AgentResponse,
)
async def run_engineering_agent(
    payload: AgentRequest,
    current_user: User = Depends(get_current_user),
) -> AgentResponse:
    orchestrator = EngineeringOrchestrator()

    result = await orchestrator.run_agent(
        agent_name=payload.agent,
        task=payload.task,
    )

    return AgentResponse(**result)


@router.post(
    "/agent-with-tool",
    response_model=ToolAgentResponse,
)
async def run_engineering_agent_with_tool(
    payload: ToolAgentRequest,
    current_user: User = Depends(get_current_user),
) -> ToolAgentResponse:
    orchestrator = EngineeringOrchestrator()

    result = await orchestrator.run_agent_with_tool(
        agent_name=payload.agent,
        task=payload.task,
        tool_name=payload.tool,
        tool_query=payload.tool_query,
    )

    return ToolAgentResponse(**result)


@router.post(
    "/agent-auto",
    response_model=AutoToolAgentResponse,
)
async def run_engineering_agent_auto(
    payload: AutoToolAgentRequest,
    current_user: User = Depends(get_current_user),
) -> AutoToolAgentResponse:
    orchestrator = EngineeringOrchestrator()

    result = await orchestrator.run_agent_auto(
        agent_name=payload.agent,
        task=payload.task,
    )

    return AutoToolAgentResponse(**result)


@router.post(
    "/analyze-project",
    response_model=ProjectAnalysisResponse,
)
async def analyze_project(
    payload: ProjectAnalysisRequest,
    current_user: User = Depends(get_current_user),
) -> ProjectAnalysisResponse:
    orchestrator = EngineeringOrchestrator()

    result = await orchestrator.analyze_project(
        project_description=payload.project_description,
    )

    return ProjectAnalysisResponse(**result)