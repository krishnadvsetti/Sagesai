def test_security_headers_are_present(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert (
        response.headers["x-content-type-options"]
        == "nosniff"
    )
    assert response.headers["x-frame-options"] == "DENY"
    assert (
        response.headers["referrer-policy"]
        == "strict-origin-when-cross-origin"
    )
    assert "permissions-policy" in response.headers


def test_request_id_is_generated(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["x-request-id"]
    assert response.headers["x-correlation-id"]


def test_correlation_id_is_propagated(client):
    correlation_id = "pytest-correlation-123"

    response = client.get(
        "/api/v1/health",
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["x-correlation-id"]
        == correlation_id
    )