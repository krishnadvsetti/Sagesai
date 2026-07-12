import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import (
    ApprovalRequest,
    ApprovalStatus,
)


class ApprovalService:
    async def create_request(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        action_type: str,
        description: str,
        action_payload: dict,
    ) -> ApprovalRequest:
        approval = ApprovalRequest(
            requested_by=user_id,
            action_type=action_type,
            description=description,
            action_payload=action_payload,
        )

        db.add(approval)
        await db.commit()
        await db.refresh(approval)

        return approval

    async def get_request(
        self,
        db: AsyncSession,
        approval_id: uuid.UUID,
    ) -> ApprovalRequest | None:
        result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == approval_id
            )
        )

        return result.scalar_one_or_none()

    async def approve(
        self,
        db: AsyncSession,
        approval_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        comment: str | None,
    ) -> ApprovalRequest:
        approval = await self.get_request(
            db,
            approval_id,
        )

        if approval is None:
            raise ValueError("Approval request not found")

        if approval.status != ApprovalStatus.PENDING:
            raise ValueError(
                "Only pending requests can be approved"
            )

        approval.status = ApprovalStatus.APPROVED
        approval.reviewed_by = reviewer_id
        approval.review_comment = comment
        approval.reviewed_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(approval)

        return approval

    async def reject(
        self,
        db: AsyncSession,
        approval_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        comment: str | None,
    ) -> ApprovalRequest:
        approval = await self.get_request(
            db,
            approval_id,
        )

        if approval is None:
            raise ValueError("Approval request not found")

        if approval.status != ApprovalStatus.PENDING:
            raise ValueError(
                "Only pending requests can be rejected"
            )

        approval.status = ApprovalStatus.REJECTED
        approval.reviewed_by = reviewer_id
        approval.review_comment = comment
        approval.reviewed_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(approval)

        return approval

    async def execute(
        self,
        db: AsyncSession,
        approval_id: uuid.UUID,
    ) -> ApprovalRequest:
        approval = await self.get_request(
            db,
            approval_id,
        )

        if approval is None:
            raise ValueError("Approval request not found")

        if approval.status != ApprovalStatus.APPROVED:
            raise ValueError(
                "Action must be approved before execution"
            )

        approval.status = ApprovalStatus.EXECUTED
        approval.executed_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(approval)

        return approval