from unittest.mock import Mock

import numpy as np
import pytest
import torch
from torch import nn

from app.api.v1.endpoints import soc as soc_endpoint
from app.ml.anomaly.data.generate import FEATURES
from app.ml.anomaly.inference import AnomalyDetector


class ZeroReconstructionModel(nn.Module):
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return torch.zeros_like(inputs)


def build_detector(threshold: float = 0.5) -> AnomalyDetector:
    detector = AnomalyDetector.__new__(AnomalyDetector)

    detector.threshold = threshold
    detector.scaler = Mock()
    detector.scaler.transform.side_effect = lambda values: values
    detector.model = ZeroReconstructionModel()

    return detector


def valid_features() -> dict[str, float]:
    return {
        "failed_logins": 1.0,
        "login_hour": 2.0,
        "request_rate": 1.0,
        "unique_ips": 1.0,
        "privilege_actions": 0.0,
        "data_transfer_mb": 1.0,
    }


def test_anomaly_detector_returns_expected_result():
    detector = build_detector(threshold=0.5)

    result = detector.predict(valid_features())

    expected_values = np.array(
        [[valid_features()[name] for name in FEATURES]],
        dtype=np.float32,
    )

    expected_score = float(np.mean(expected_values**2))

    assert result["anomaly_score"] == pytest.approx(
        expected_score
    )
    assert result["threshold"] == 0.5
    assert result["is_anomaly"] is True


def test_anomaly_detector_marks_normal_event():
    detector = build_detector(threshold=1000.0)

    result = detector.predict(valid_features())

    assert result["is_anomaly"] is False


def test_detect_anomaly_endpoint(
    client,
    authenticate_as_admin,
    monkeypatch,
):
    monkeypatch.setattr(
        soc_endpoint.anomaly_detector,
        "predict",
        Mock(
            return_value={
                "is_anomaly": True,
                "anomaly_score": 0.92,
                "threshold": 0.5,
            }
        ),
    )

    response = client.post(
        "/api/v1/soc/detect-anomaly",
        json=valid_features(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_anomaly"] is True
    assert data["anomaly_score"] == pytest.approx(0.92)
    assert data["threshold"] == pytest.approx(0.5)


def test_detect_anomaly_requires_authorization(client):
    response = client.post(
        "/api/v1/soc/detect-anomaly",
        json=valid_features(),
    )

    assert response.status_code == 401


def test_detect_anomaly_validates_input(
    client,
    authenticate_as_admin,
):
    payload = valid_features()
    payload["login_hour"] = 25.0

    response = client.post(
        "/api/v1/soc/detect-anomaly",
        json=payload,
    )

    assert response.status_code == 422