from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.users import UserService


class DummyUser:
    def __init__(self, username: str) -> None:
        self.user_id = uuid4()
        self.username = username
        self.created_at = datetime.now(UTC)


def _set_api_key(monkeypatch, value: str | None) -> None:
    if value is None:
        monkeypatch.delenv("KLUG_API_KEY", raising=False)
    else:
        monkeypatch.setenv("KLUG_API_KEY", value)
    get_settings.cache_clear()


def test_write_endpoint_requires_api_key_when_configured(monkeypatch) -> None:
    _set_api_key(monkeypatch, "secret-key")
    monkeypatch.setattr(
        UserService,
        "create_user",
        lambda _session, username: DummyUser(username),
    )

    client = TestClient(app)
    response = client.post("/api/v1/users", json={"username": "alice"})

    assert response.status_code == 401


def test_write_endpoint_rejects_invalid_api_key(monkeypatch) -> None:
    _set_api_key(monkeypatch, "secret-key")
    monkeypatch.setattr(
        UserService,
        "create_user",
        lambda _session, username: DummyUser(username),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/users",
        json={"username": "alice"},
        headers={"X-API-Key": "bad-key"},
    )

    assert response.status_code == 401


def test_write_endpoint_accepts_valid_api_key(monkeypatch) -> None:
    _set_api_key(monkeypatch, "secret-key")
    monkeypatch.setattr(
        UserService,
        "create_user",
        lambda _session, username: DummyUser(username),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/users",
        json={"username": "alice"},
        headers={"X-API-Key": "secret-key"},
    )

    assert response.status_code == 201


def test_write_endpoint_allows_requests_when_api_key_not_configured(monkeypatch) -> None:
    _set_api_key(monkeypatch, None)
    monkeypatch.setattr(
        UserService,
        "create_user",
        lambda _session, username: DummyUser(username),
    )

    client = TestClient(app)
    response = client.post("/api/v1/users", json={"username": "alice"})

    assert response.status_code == 201
