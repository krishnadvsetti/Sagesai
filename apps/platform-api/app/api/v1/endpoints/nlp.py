from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.nlp import (
    EntityExtractionRequest,
    EntityExtractionResponse,
)
from app.services.nlp.entity_extractor import EntityExtractor


router = APIRouter(
    prefix="/nlp",
    tags=["NLP & Transformers"],
)

entity_extractor = EntityExtractor()


@router.post(
    "/extract-entities",
    response_model=EntityExtractionResponse,
)
async def extract_entities(
    payload: EntityExtractionRequest,
    current_user: User = Depends(get_current_user),
) -> EntityExtractionResponse:
    entities = entity_extractor.extract(payload.text)

    return EntityExtractionResponse(
        entities=entities,
        entity_count=len(entities),
    )