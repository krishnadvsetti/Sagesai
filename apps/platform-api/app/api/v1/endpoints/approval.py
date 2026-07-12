import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import (
    get_current_user,
    require_roles,
)
from app.database.session import get_db
from app.models.user import User, UserRole
from app.schemas.approval import (
    ApprovalCreate,
    ApprovalExecutionResponse,
    ApprovalResponse,
    ApprovalReview,
)
from app.services.approval import ApprovalService


router = APIRouter(
    prefix="/approvals",
    tags=["Human-in-the-Loop Approvals"],
)

approval_service = ApprovalService()


@router.post(
    "",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_approval_request(
    payload: ApprovalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApprovalResponse:
    approval = await approval_service.create_request(
        db=db,
        user_id=current_user.id,
        action_type=payload.action_type,
        description=payload.description,
        action_payload=payload.action_payload,
    )

    return ApprovalResponse.model_validate(approval)


@router.post(
    "/{approval_id}/approve",
    response_model=ApprovalResponse,
)
async def approve_request(
    approval_id: uuid.UUID,
    payload: ApprovalReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
) -> ApprovalResponse:
    try:
        approval = await approval_service.approve(
            db=db,
            approval_id=approval_id,
            reviewer_id=current_user.id,
            comment=payload.comment,
        )

        return ApprovalResponse.model_validate(approval)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{approval_id}/reject",
    response_model=ApprovalResponse,
)
async def reject_request(
    approval_id: uuid.UUID,
    payload: ApprovalReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
) -> ApprovalResponse:
    try:
        approval = await approval_service.reject(
            db=db,
            approval_id=approval_id,
            reviewer_id=current_user.id,
            comment=payload.comment,
        )

        return ApprovalResponse.model_validate(approval)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{approval_id}/execute",
    response_model=ApprovalExecutionResponse,
)
async def execute_approved_action(
    approval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
) -> ApprovalExecutionResponse:
    try:
        approval = await approval_service.execute(
            db=db,
            approval_id=approval_id,
        )

        return ApprovalExecutionResponse(
            id=approval.id,
            status=approval.status,
            message="Approved action executed successfully",
            action_payload=approval.action_payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc