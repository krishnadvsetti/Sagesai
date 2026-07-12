from collections.abc import Generator
from unittest.mock import AsyncMock
import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.database.session import get_db
from app.main import app
from app.models.user import User, UserRole


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def fake_db() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def analyst_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="analyst@example.com",
        full_name="Test Analyst",
        hashed_password="test",
        role=UserRole.ANALYST,
        is_active=True,
    )


@pytest.fixture
def admin_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="admin@example.com",
        full_name="Test Admin",
        hashed_password="test",
        role=UserRole.ADMIN,
        is_active=True,
    )


@pytest.fixture
def override_db(fake_db):
    async def _get_db():
        yield fake_db

    app.dependency_overrides[get_db] = _get_db

    yield fake_db

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def authenticate_as_analyst(analyst_user):
    async def _current_user():
        return analyst_user

    app.dependency_overrides[get_current_user] = _current_user

    yield analyst_user

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def authenticate_as_admin(admin_user):
    async def _current_user():
        return admin_user

    app.dependency_overrides[get_current_user] = _current_user

    yield admin_user

    app.dependency_overrides.pop(get_current_user, None)