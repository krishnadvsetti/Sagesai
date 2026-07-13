from unittest.mock import AsyncMock

import httpx
import pytest

from app.api.v1.endpoints import soc as soc_endpoint
from app.services.anomaly.client import (
    AnomalyServiceClient,
    AnomalyServiceError,
)


def valid_features() -> dict[str, float]:
    return {
        "failed_logins": 1.0,
        "login_hour": 2.0,
        "request_rate": 1.0,
        "unique_ips": 1.0,
        "privilege_actions": 0.0,
        "data_transfer_mb": 1.0,
    }


@pytest.mark.asyncio
async def test_anomaly_service_client_returns_prediction(monkeypatch):
    expected = {
        "is_anomaly": True,
        "anomaly_score": 0.92,
        "threshold": 0.5,
    }

    response = httpx.Response(
        200,
        json=expected,
        request=httpx.Request(
            "POST",
            "http://anomaly-service:8001/predict",
        ),
    )

    request_mock = AsyncMock(return_value=response)

    monkeypatch.setattr(
        httpx.AsyncClient,
        "post",
        request_mock,
    )

    client = AnomalyServiceClient()
    result = await client.predict(valid_features())

    assert result == expected


@pytest.mark.asyncio
async def test_anomaly_service_client_handles_failure(monkeypatch):
    request_mock = AsyncMock(
        side_effect=httpx.ConnectError(
            "Connection failed",
            request=httpx.Request(
                "POST",
                "http://anomaly-service:8001/predict",
            ),
        )
    )

    monkeypatch.setattr(
        httpx.AsyncClient,
        "post",
        request_mock,
    )

    client = AnomalyServiceClient()

    with pytest.raises(
        AnomalyServiceError,
        match="Anomaly detection service is unavailable",
    ):
        await client.predict(valid_features())


def test_detect_anomaly_endpoint(
    client,
    authenticate_as_admin,
    monkeypatch,
):
    monkeypatch.setattr(
        soc_endpoint.anomaly_client,
        "predict",
        AsyncMock(
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
