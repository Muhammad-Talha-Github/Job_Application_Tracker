"""Tests for authentication, validation, application CRUD, and ownership."""

from datetime import datetime, timedelta, timezone

import jwt

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.models.user import User


def test_registration_validates_email_password_and_hides_password(client, test_session_factory):
    """Registration creates a user, stores a hash, and returns no secret fields."""
    password = "a strong learning password"
    response = client.post(
        "/auth/register",
        json={"email": "student@example.com", "password": password},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "student@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    # Check the database contains a hash rather than the original password.
    with test_session_factory() as db:
        user = db.query(User).filter_by(email="student@example.com").one()
        assert user.password_hash != password
        assert user.password_hash.startswith("$argon2")

    assert client.post(
        "/auth/register", json={"email": "STUDENT@example.com", "password": password}
    ).status_code == 409
    assert client.post(
        "/auth/register", json={"email": "not-an-email", "password": password}
    ).status_code == 422
    assert client.post(
        "/auth/register", json={"email": "short@example.com", "password": "short"}
    ).status_code == 422


def test_login_accepts_correct_credentials_and_rejects_wrong_credentials(client):
    """Login returns a bearer token only when both email and password are valid."""
    password = "a strong learning password"
    client.post("/auth/register", json={"email": "login@example.com", "password": password})

    response = client.post(
        "/auth/login", json={"email": "login@example.com", "password": password}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"

    assert client.post(
        "/auth/login", json={"email": "login@example.com", "password": "incorrect password"}
    ).status_code == 401
    assert client.post(
        "/auth/login", json={"email": "unknown@example.com", "password": password}
    ).status_code == 401


def test_protected_route_rejects_missing_invalid_and_expired_tokens(client):
    """Application routes require a valid, non-expired bearer JWT."""
    assert client.get("/applications").status_code == 401
    assert client.get(
        "/applications", headers={"Authorization": "Bearer not-a-jwt"}
    ).status_code == 401


def test_cors_allows_local_frontend_and_rejects_unconfigured_origins(client):
    """CORS allows configured local UI origins without enabling every website."""
    allowed = client.options(
        "/applications",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"

    denied = client.options(
        "/applications",
        headers={
            "Origin": "https://unconfigured.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in denied.headers

    expired_token = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    assert client.get(
        "/applications", headers={"Authorization": f"Bearer {expired_token}"}
    ).status_code == 401


def test_application_crud_and_missing_ids(client, user_a_headers, application_payload):
    """An authenticated user can create, list, read, replace, and delete an application."""
    assert client.get("/applications", headers=user_a_headers).json() == []

    created_response = client.post(
        "/applications", json=application_payload, headers=user_a_headers
    )
    assert created_response.status_code == 201
    created = created_response.json()
    application_id = created["id"]
    assert created["company"] == application_payload["company"]
    assert "user_id" not in created
    assert [item["id"] for item in client.get(
        "/applications", headers=user_a_headers
    ).json()] == [application_id]

    fetched = client.get(f"/applications/{application_id}", headers=user_a_headers)
    assert fetched.status_code == 200
    assert fetched.json()["position"] == "Software Engineer"

    updated_payload = {**application_payload, "position": "Senior Engineer"}
    updated = client.put(
        f"/applications/{application_id}", json=updated_payload, headers=user_a_headers
    )
    assert updated.status_code == 200
    assert updated.json()["position"] == "Senior Engineer"

    deleted = client.delete(f"/applications/{application_id}", headers=user_a_headers)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/applications/{application_id}", headers=user_a_headers).status_code == 404
    assert client.get("/applications/99999", headers=user_a_headers).status_code == 404
    assert client.put(
        "/applications/99999", json=application_payload, headers=user_a_headers
    ).status_code == 404
    assert client.delete("/applications/99999", headers=user_a_headers).status_code == 404


def test_application_validation_rejects_invalid_fields(client, user_a_headers, application_payload):
    """Pydantic rejects missing fields, unknown statuses, malformed dates, and URLs."""
    invalid_payloads = [
        {**application_payload, "status": "Considering"},
        {**application_payload, "application_date": "not-a-date"},
        {**application_payload, "job_url": "not-a-url"},
        {key: value for key, value in application_payload.items() if key != "company"},
    ]

    for payload in invalid_payloads:
        response = client.post("/applications", json=payload, headers=user_a_headers)
        assert response.status_code == 422

    assert client.get("/applications", headers=user_a_headers).json() == []


def test_application_cannot_be_read_updated_or_deleted_by_another_user(
    client, user_a_headers, user_b_headers, application_payload
):
    """Ownership checks hide another user's application and prevent all changes."""
    payload_with_forged_owner = {**application_payload, "user_id": 99999}
    created = client.post(
        "/applications", json=payload_with_forged_owner, headers=user_a_headers
    )
    assert created.status_code == 201
    application_id = created.json()["id"]

    assert [item["id"] for item in client.get(
        "/applications", headers=user_a_headers
    ).json()] == [application_id]
    assert client.get("/applications", headers=user_b_headers).json() == []
    assert client.get(f"/applications/{application_id}", headers=user_b_headers).status_code == 404
    assert client.put(
        f"/applications/{application_id}",
        json={**application_payload, "position": "Changed by B"},
        headers=user_b_headers,
    ).status_code == 404
    assert client.delete(
        f"/applications/{application_id}", headers=user_b_headers
    ).status_code == 404

    # The denied attempts left the owner's record unchanged and available.
    owner_record = client.get(f"/applications/{application_id}", headers=user_a_headers)
    assert owner_record.status_code == 200
    assert owner_record.json()["position"] == application_payload["position"]
