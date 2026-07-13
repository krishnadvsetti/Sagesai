from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
import uuid

from app.api.v1.endpoints import memory as memory_endpoint


def test_create_memory_session(
    client,
    override_db,
    authenticate_as_analyst,
    monkeypatch,
):
    session_id = uuid.uuid4()

    mock_session = SimpleNamespace(
        id=session_id,
        title="Architecture discussion",
        created_at=datetime.now(UTC),
    )

    mock_create = AsyncMock(return_value=mock_session)

    mock_service = Mock()
    mock_service.create_session = mock_create

    monkeypatch.setattr(
        memory_endpoint,
        "get_memory_service",
        lambda: mock_service,
    )

    response = client.post(
        "/api/v1/memory/sessions",
        json={"title": "Architecture discussion"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == str(session_id)
    assert data["title"] == "Architecture discussion"

    mock_create.assert_awaited_once()


def test_memory_history_not_found(
    client,
    override_db,
    authenticate_as_analyst,
    monkeypatch,
):
    mock_service = Mock()
    mock_service.get_user_session = AsyncMock(return_value=None)

    monkeypatch.setattr(
        memory_endpoint,
        "get_memory_service",
        lambda: mock_service,
    )

    response = client.get(
        f"/api/v1/memory/sessions/{uuid.uuid4()}/history"
    )

    assert response.status_code == 404
    assert response.json()["error"]["message"] == (
        "Conversation session not found"
    )