import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.information import (
    AskRequest,
    AskResponse,
    DocumentUploadResponse,
    SearchRequest,
    SearchResponse,
)
from app.services.ai.gateway import AIGateway
from app.services.rag.pipeline import RAGPipeline

router = APIRouter(
    prefix="/information",
    tags=["Information Manager"],
)

rag_pipeline = RAGPipeline()


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    filename = file.filename or "document"

    if Path(filename).suffix.lower() not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported",
        )

    document_id = str(uuid.uuid4())

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=Path(filename).suffix,
    ) as temporary_file:
        shutil.copyfileobj(file.file, temporary_file)
        temporary_path = Path(temporary_file.name)

    try:
        chunks_created = rag_pipeline.ingest(
            file_path=temporary_path,
            document_id=document_id,
            filename=filename,
        )
    finally:
        temporary_path.unlink(missing_ok=True)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        chunks_created=chunks_created,
    )


@router.post("/search", response_model=SearchResponse)
async def semantic_search(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user),
) -> SearchResponse:
    results = rag_pipeline.search(
        query=payload.query,
        limit=payload.limit,
    )

    return SearchResponse(
        query=payload.query,
        results=results,
    )


@router.post("/ask", response_model=AskResponse)
async def ask_information(
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
) -> AskResponse:
    sources = rag_pipeline.search(
        query=payload.question,
        limit=payload.limit,
    )

    if not sources:
        raise HTTPException(
            status_code=404,
            detail="No relevant information found",
        )

    context = "\n\n".join(
        f"[Source {index + 1}]\n{source['content']}"
        for index, source in enumerate(sources)
    )

    prompt = f"""
Answer the question using only the provided context.

If the answer cannot be determined from the context, say that the
available documents do not contain enough information.

Context:
{context}

Question:
{payload.question}
"""

    gateway = AIGateway()

    answer = await gateway.generate(
        prompt=prompt,
        system_instruction=(
            "You are Sagesai's enterprise information assistant. "
            "Provide accurate, grounded answers based only on retrieved context."
        ),
    )

    return AskResponse(
        question=payload.question,
        answer=answer,
        sources=sources,
    )