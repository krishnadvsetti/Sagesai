import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.approval import ApprovalStatus


class ApprovalCreate(BaseModel):
    action_type: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=5000)
    action_payload: dict = Field(default_factory=dict)


class ApprovalReview(BaseModel):
    comment: str | None = Field(
        default=None,
        max_length=5000,
    )


class ApprovalResponse(BaseModel):
    id: uuid.UUID
    requested_by: uuid.UUID
    action_type: str
    description: str
    action_payload: dict
    status: ApprovalStatus
    reviewed_by: uuid.UUID | None
    review_comment: str | None
    created_at: datetime
    reviewed_at: datetime | None
    executed_at: datetime | None

    model_config = {"from_attributes": True}


class ApprovalExecutionResponse(BaseModel):
    id: uuid.UUID
    status: ApprovalStatus
    message: str
    action_payload: dict