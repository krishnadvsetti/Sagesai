from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.engineering.orchestrator import (
    EngineeringOrchestrator,
)
from app.services.engineering.tool_selector import ToolSelector


def build_orchestrator() -> EngineeringOrchestrator:
    orchestrator = EngineeringOrchestrator.__new__(
        EngineeringOrchestrator
    )

    orchestrator.gateway = AsyncMock()
    orchestrator.tool_registry = AsyncMock()
    orchestrator.tool_selector = AsyncMock()

    orchestrator.agents = {
        "architecture": SimpleNamespace(
            name="architecture_agent",
            run=AsyncMock(
                return_value="Architecture result"
            ),
        )
    }

    return orchestrator


@pytest.mark.asyncio
async def test_engineering_agent_runs():
    orchestrator = build_orchestrator()

    result = await orchestrator.run_agent(
        agent_name="architecture",
        task="Design the platform",
    )

    assert result["agent"] == "architecture_agent"
    assert result["result"] == "Architecture result"


@pytest.mark.asyncio
async def test_unknown_engineering_agent_is_rejected():
    orchestrator = build_orchestrator()

    with pytest.raises(
        ValueError,
        match="Unknown agent",
    ):
        await orchestrator.run_agent(
            agent_name="unknown",
            task="Test task",
        )


@pytest.mark.asyncio
async def test_auto_tool_selection_none():
    orchestrator = build_orchestrator()

    orchestrator.tool_selector.select.return_value = {
        "tool": "none",
        "query": "general architecture",
    }

    result = await orchestrator.run_agent_auto(
        agent_name="architecture",
        task="Explain microservices",
    )

    assert result["selected_tool"] == "none"
    assert result["tool_result"] is None


@pytest.mark.asyncio
async def test_auto_tool_selection_uses_repository_search():
    orchestrator = build_orchestrator()

    orchestrator.tool_selector.select.return_value = {
        "tool": "repository_search",
        "query": "FastAPI usage",
    }

    orchestrator.tool_registry.execute.return_value = {
        "matches": [{"file": "app/main.py"}]
    }

    result = await orchestrator.run_agent_auto(
        agent_name="architecture",
        task="Find FastAPI usage",
    )

    assert result["selected_tool"] == "repository_search"

    orchestrator.tool_registry.execute.assert_awaited_once_with(
        "repository_search",
        query="FastAPI usage",
        max_results=5,
    )


@pytest.mark.asyncio
async def test_tool_selector_parses_valid_json():
    gateway = AsyncMock()

    gateway.generate.return_value = (
        '{"tool": "repository_search", '
        '"query": "FastAPI usage"}'
    )

    selector = ToolSelector(gateway)

    result = await selector.select(
        "Find FastAPI usage in the repository"
    )

    assert result == {
        "tool": "repository_search",
        "query": "FastAPI usage",
    }


@pytest.mark.asyncio
async def test_tool_selector_rejects_invalid_tool():
    gateway = AsyncMock()

    gateway.generate.return_value = (
        '{"tool": "dangerous_tool", "query": "test"}'
    )

    selector = ToolSelector(gateway)

    with pytest.raises(
        ValueError,
        match="Invalid tool selected",
    ):
        await selector.select("Test task")