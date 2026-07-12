from jose import jwt

from app.core.config.settings import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "SecurePassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_contains_subject_and_role():
    token = create_access_token(
        subject="12345678-1234-5678-1234-567812345678",
        additional_claims={"role": "admin"},
    )

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == (
        "12345678-1234-5678-1234-567812345678"
    )
    assert payload["role"] == "admin"
    assert "iat" in payload
    assert "exp" in payload


def test_protected_endpoint_rejects_missing_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "HTTP_401"