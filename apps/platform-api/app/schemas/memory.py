import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.memory import MemoryRole


class ConversationCreate(BaseModel):
    title: str = Field(
        default="New conversation",
        min_length=1,
        max_length=255,
    )


class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MemoryMessageResponse(BaseModel):
    id: uuid.UUID
    role: MemoryRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=20_000,
    )


class ConversationChatResponse(BaseModel):
    session_id: uuid.UUID
    response: str
    history: list[MemoryMessageResponse]