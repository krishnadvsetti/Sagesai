from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.api.dependencies.auth import get_current_user
from app.ml.document_vision.inference import DocumentQualityClassifier
from app.models.user import User


router = APIRouter(
    prefix="/vision",
    tags=["Computer Vision"],
)

classifier: DocumentQualityClassifier | None = None


def get_classifier() -> DocumentQualityClassifier:
    global classifier
    if classifier is None:
        classifier = DocumentQualityClassifier()
    return classifier


@router.post("/document-quality")
async def analyze_document_quality(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    if file.content_type not in {"image/png", "image/jpeg"}:
        raise HTTPException(
            status_code=415,
            detail="Only PNG and JPEG images are supported.",
        )

    contents = await file.read()

    try:
        image = Image.open(BytesIO(contents))
        result = get_classifier().predict(image)
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file.",
        ) from exc

    return {
        "filename": file.filename,
        **result,
    }