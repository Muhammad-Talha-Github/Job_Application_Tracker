"""Shared test setup and fixtures for the FastAPI test suite."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 - imports all models so SQLAlchemy sees their tables
from app.database import Base, get_db
from app.main import app


@pytest.fixture
def test_engine():
    """Create a brand-new in-memory SQLite database for one test."""
    # This engine is separate from the PostgreSQL engine used by the running app.
    # StaticPool keeps this in-memory database alive across TestClient connections.
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_session_factory(test_engine):
    """Make short-lived SQLAlchemy sessions connected only to the test database."""
    return sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture
def client(test_session_factory):
    """Send requests to FastAPI while overriding its DB dependency with SQLite."""
    def override_get_db():
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    # Restore any pre-existing overrides instead of leaving global test state behind.
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


@pytest.fixture
def application_payload():
    """A valid request body that tests can copy and adjust for each case."""
    return {
        "company": "Example Company",
        "position": "Software Engineer",
        "status": "Applied",
        "application_date": "2026-10-07",
        "job_url": "https://jobs.example.com/role",
        "notes": "Follow up next week",
    }


def create_user_and_get_headers(client, email: str) -> dict[str, str]:
    """Register a test user, log in, and return its bearer authorization header."""
    password = "a strong learning password"
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 201
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_a_headers(client):
    """An authenticated header for the first test user."""
    return create_user_and_get_headers(client, "owner-a@example.com")


@pytest.fixture
def user_b_headers(client):
    """An authenticated header for a second, separate test user."""
    return create_user_and_get_headers(client, "owner-b@example.com")
