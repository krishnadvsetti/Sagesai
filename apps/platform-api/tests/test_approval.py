from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

from app.api.v1.endpoints import approval as approval_endpoint
from app.models.approval import ApprovalStatus


def make_approval(
    *,
    requested_by: uuid.UUID,
    status: ApprovalStatus,
    reviewed_by: uuid.UUID | None = None,
):
    return SimpleNamespace(
        id=uuid.uuid4(),
        requested_by=requested_by,
        action_type="deploy_service",
        description="Deploy service to production",
        action_payload={"service": "platform-api"},
        status=status,
        reviewed_by=reviewed_by,
        review_comment=None,
        created_at=datetime.now(UTC),
        reviewed_at=None,
        executed_at=None,
    )


def test_create_approval_request(
    client,
    override_db,
    authenticate_as_analyst,
    analyst_user,
    monkeypatch,
):
    approval = make_approval(
        requested_by=analyst_user.id,
        status=ApprovalStatus.PENDING,
    )

    monkeypatch.setattr(
        approval_endpoint.approval_service,
        "create_request",
        AsyncMock(return_value=approval),
    )

    response = client.post(
        "/api/v1/approvals",
        json={
            "action_type": "deploy_service",
            "description": "Deploy service to production",
            "action_payload": {
                "service": "platform-api",
            },
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_analyst_cannot_approve_request(
    client,
    override_db,
    authenticate_as_analyst,
):
    response = client.post(
        f"/api/v1/approvals/{uuid.uuid4()}/approve",
        json={"comment": "Approved"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "HTTP_403"


def test_admin_can_approve_request(
    client,
    override_db,
    authenticate_as_admin,
    admin_user,
    monkeypatch,
):
    approval = make_approval(
        requested_by=uuid.uuid4(),
        status=ApprovalStatus.APPROVED,
        reviewed_by=admin_user.id,
    )

    approval.review_comment = "Approved for deployment"
    approval.reviewed_at = datetime.now(UTC)

    monkeypatch.setattr(
        approval_endpoint.approval_service,
        "approve",
        AsyncMock(return_value=approval),
    )

    response = client.post(
        f"/api/v1/approvals/{approval.id}/approve",
        json={"comment": "Approved for deployment"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert response.json()["reviewed_by"] == str(admin_user.id)