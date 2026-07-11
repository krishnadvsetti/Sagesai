from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.core.config.settings import settings
from app.models.user import User
from app.schemas.ai import GenerateRequest, GenerateResponse
from app.services.ai.gateway import AIGateway

router = APIRouter(prefix="/ai", tags=["AI Gateway"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    payload: GenerateRequest,
    current_user: User = Depends(get_current_user),
) -> GenerateResponse:
    gateway = AIGateway()

    content = await gateway.generate(
        prompt=payload.prompt,
        system_instruction=payload.system_instruction,
    )

    return GenerateResponse(
        model=settings.AI_MODEL,
        content=content,
    )