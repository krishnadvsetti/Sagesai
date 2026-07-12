def test_not_found_returns_standard_error(client):
    response = client.get(
        "/api/v1/does-not-exist",
        headers={
            "X-Correlation-ID": "pytest-correlation-id",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "HTTP_404"
    assert data["error"]["message"] == "Not Found"
    assert data["error"]["correlation_id"] == (
        "pytest-correlation-id"
    )
    assert data["error"]["request_id"]


def test_unauthorized_returns_standard_error(client):
    response = client.post(
        "/api/v1/information/search",
        json={},
    )

    assert response.status_code == 401

    data = response.json()

    assert data["error"]["code"] == "HTTP_401"