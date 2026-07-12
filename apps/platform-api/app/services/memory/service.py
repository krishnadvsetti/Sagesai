import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import (
    ConversationSession,
    MemoryMessage,
    MemoryRole,
)
from app.services.ai.gateway import AIGateway


class MemoryService:
    def __init__(self) -> None:
        self.gateway = AIGateway()

    async def create_session(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
    ) -> ConversationSession:
        session = ConversationSession(
            user_id=user_id,
            title=title,
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return session

    async def get_user_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ConversationSession | None:
        result = await db.execute(
            select(ConversationSession).where(
                ConversationSession.id == session_id,
                ConversationSession.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_history(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        limit: int = 20,
    ) -> list[MemoryMessage]:
        result = await db.execute(
            select(MemoryMessage)
            .where(
                MemoryMessage.session_id == session_id
            )
            .order_by(MemoryMessage.created_at.desc())
            .limit(limit)
        )

        messages = list(result.scalars().all())
        messages.reverse()

        return messages

    async def add_message(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        role: MemoryRole,
        content: str,
    ) -> MemoryMessage:
        message = MemoryMessage(
            session_id=session_id,
            role=role,
            content=content,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message

    async def chat(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        message: str,
    ) -> dict:
        session = await self.get_user_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise ValueError("Conversation session not found")

        history = await self.get_history(
            db=db,
            session_id=session_id,
        )

        history_text = "\n".join(
            f"{item.role.value}: {item.content}"
            for item in history
        )

        await self.add_message(
            db=db,
            session_id=session_id,
            role=MemoryRole.USER,
            content=message,
        )

        prompt = f"""
CONVERSATION HISTORY:
{history_text}

CURRENT USER MESSAGE:
{message}

Respond to the current user message while using the
conversation history when it is relevant.
"""

        response = await self.gateway.generate(
            prompt=prompt,
            system_instruction=(
                "You are the Sagesai enterprise AI assistant. "
                "Use conversation memory accurately. "
                "Do not invent facts that are not present in "
                "the conversation or available context."
            ),
        )

        await self.add_message(
            db=db,
            session_id=session_id,
            role=MemoryRole.ASSISTANT,
            content=response,
        )

        updated_history = await self.get_history(
            db=db,
            session_id=session_id,
        )

        return {
            "session_id": session_id,
            "response": response,
            "history": updated_history,
        }