def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "Sagesai"
    assert "version" in data
    assert "timestamp" in data


def test_liveness_check(client):
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "alive"
    assert data["service"] == "Sagesai"