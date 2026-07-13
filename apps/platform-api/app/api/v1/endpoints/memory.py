import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.memory import (
    ConversationChatRequest,
    ConversationChatResponse,
    ConversationCreate,
    ConversationResponse,
    MemoryMessageResponse,
)
from app.services.memory import MemoryService


router = APIRouter(
    prefix="/memory",
    tags=["AI Memory"],
)

memory_service: MemoryService | None = None


def get_memory_service() -> MemoryService:
    global memory_service
    if memory_service is None:
        memory_service = MemoryService()
    return memory_service


@router.post(
    "/sessions",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationResponse:
    session = await get_memory_service().create_session(
        db=db,
        user_id=current_user.id,
        title=payload.title,
    )

    return ConversationResponse.model_validate(session)


@router.get(
    "/sessions/{session_id}/history",
    response_model=list[MemoryMessageResponse],
)
async def get_conversation_history(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MemoryMessageResponse]:
    session = await get_memory_service().get_user_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation session not found",
        )

    history = await get_memory_service().get_history(
        db=db,
        session_id=session_id,
    )

    return [
        MemoryMessageResponse.model_validate(message)
        for message in history
    ]


@router.post(
    "/sessions/{session_id}/chat",
    response_model=ConversationChatResponse,
)
async def chat_with_memory(
    session_id: uuid.UUID,
    payload: ConversationChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationChatResponse:
    try:
        result = await get_memory_service().chat(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            message=payload.message,
        )

        return ConversationChatResponse(
            session_id=result["session_id"],
            response=result["response"],
            history=[
                MemoryMessageResponse.model_validate(message)
                for message in result["history"]
            ],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc