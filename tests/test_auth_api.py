from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.users import UserService


class DummyUser:
    def __init__(self, username: str) -> None:
        self.user_id = uuid4()
        self.username = username
        self.created_at = datetime.now(UTC)


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _set_auth(
    monkeypatch, *, api_key: str | None, auth_mode: str | None = None
) -> None:
    if api_key is None:
        monkeypatch.delenv("KLUG_API_KEY", raising=False)
    else:
        monkeypatch.setenv("KLUG_API_KEY", api_key)
    if auth_mode is None:
        monkeypatch.delenv("KLUG_API_AUTH_MODE", raising=False)
    else:
        monkeypatch.setenv("KLUG_API_AUTH_MODE", auth_mode)
    get_settings.cache_clear()


def test_write_endpoint_requires_api_key_when_configured(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="write")
    monkeypatch.setattr(
        UserService,
        "create_user",
        lambda _session, username: DummyUser(username),
    )

    client = TestClient(app)
    response = client.post("/api/v1/users", json={"username": "alice"})

    assert response.status_code == 401


def test_write_endpoint_rejects_invalid_api_key(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="write")
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
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="write")
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
    _set_auth(monkeypatch, api_key=None, auth_mode="write")
    monkeypatch.setattr(
        UserService,
        "create_user",
        lambda _session, username: DummyUser(username),
    )

    client = TestClient(app)
    response = client.post("/api/v1/users", json={"username": "alice"})

    assert response.status_code == 201


def test_read_endpoint_allowed_in_write_mode_without_api_key(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="write")
    monkeypatch.setattr(UserService, "list_users", lambda _session: [])

    client = TestClient(app)
    response = client.get("/api/v1/users")

    assert response.status_code == 200


def test_read_endpoint_requires_api_key_in_all_mode(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="all")
    monkeypatch.setattr(UserService, "list_users", lambda _session: [])

    client = TestClient(app)
    response = client.get("/api/v1/users")

    assert response.status_code == 401


def test_read_endpoint_accepts_api_key_in_all_mode(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="all")
    monkeypatch.setattr(UserService, "list_users", lambda _session: [])

    client = TestClient(app)
    response = client.get("/api/v1/users", headers={"X-API-Key": "secret-key"})

    assert response.status_code == 200


def test_disabled_mode_ignores_api_key_requirement(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="disabled")
    monkeypatch.setattr(UserService, "list_users", lambda _session: [])

    client = TestClient(app)
    response = client.get("/api/v1/users")

    assert response.status_code == 200


def test_all_mode_allows_session_cookie_auth(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="all")
    monkeypatch.setenv("KLUG_SESSION_PASSWORD", "session-pass")
    monkeypatch.setenv("KLUG_SESSION_SECRET", "session-secret")
    get_settings.cache_clear()
    monkeypatch.setattr(UserService, "list_users", lambda _session: [])

    client = TestClient(app)
    login = client.post("/api/v1/session/login", json={"password": "session-pass"})
    assert login.status_code == 200

    response = client.get("/api/v1/users")
    assert response.status_code == 200
