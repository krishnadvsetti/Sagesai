from io import BytesIO
from unittest.mock import Mock

import numpy as np
from PIL import Image

import pytest

from app.api.v1.endpoints import vision as vision_endpoint
from app.ml.document_vision.inference import DocumentQualityClassifier


def build_classifier() -> DocumentQualityClassifier:
    classifier = DocumentQualityClassifier.__new__(
        DocumentQualityClassifier
    )

    classifier.class_names = [
        "good",
        "poor",
    ]

    classifier.model = Mock()
    classifier.model.predict.return_value = np.array(
        [[0.9, 0.1]],
        dtype=np.float32,
    )

    return classifier


def create_test_image() -> BytesIO:
    image = Image.new(
        mode="RGB",
        size=(64, 64),
        color="white",
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def test_document_quality_classifier_predicts():
    classifier = build_classifier()

    image = Image.new(
        mode="RGB",
        size=(64, 64),
        color="white",
    )

    result = classifier.predict(image)

    assert result["quality"] == "good"
    assert result["confidence"] == pytest.approx(0.9)

    assert result["probabilities"]["good"] == pytest.approx(0.9)
    assert result["probabilities"]["poor"] == pytest.approx(0.1)

    classifier.model.predict.assert_called_once()

    model_input = classifier.model.predict.call_args.args[0]

    assert model_input.shape == (1, 128, 128, 1)
    assert model_input.dtype == np.float32


def test_document_quality_endpoint(
    client,
    authenticate_as_analyst,
    monkeypatch,
):
    monkeypatch.setattr(
        vision_endpoint.classifier,
        "predict",
        Mock(
            return_value={
                "quality": "good",
                "confidence": 0.95,
                "probabilities": {
                    "good": 0.95,
                    "poor": 0.05,
                },
            }
        ),
    )

    image = create_test_image()

    response = client.post(
        "/api/v1/vision/document-quality",
        files={
            "file": (
                "document.png",
                image,
                "image/png",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "document.png"
    assert data["quality"] == "good"
    assert data["confidence"] == 0.95


def test_document_quality_rejects_unsupported_file(
    client,
    authenticate_as_analyst,
):
    response = client.post(
        "/api/v1/vision/document-quality",
        files={
            "file": (
                "document.txt",
                b"not an image",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415
    assert response.json()["error"]["message"] == (
        "Only PNG and JPEG images are supported."
    )


def test_document_quality_rejects_invalid_image(
    client,
    authenticate_as_analyst,
):
    response = client.post(
        "/api/v1/vision/document-quality",
        files={
            "file": (
                "invalid.png",
                b"this is not valid image data",
                "image/png",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["message"] == (
        "Invalid image file."
    )


def test_document_quality_requires_authentication(client):
    response = client.post(
        "/api/v1/vision/document-quality",
        files={
            "file": (
                "document.png",
                create_test_image(),
                "image/png",
            )
        },
    )

    assert response.status_code == 401