from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def _set_session_env(
    monkeypatch,
    *,
    password: str | None,
    secret: str | None,
    auth_mode: str = "write",
) -> None:
    if password is None:
        monkeypatch.delenv("KLUG_SESSION_PASSWORD", raising=False)
    else:
        monkeypatch.setenv("KLUG_SESSION_PASSWORD", password)

    if secret is None:
        monkeypatch.delenv("KLUG_SESSION_SECRET", raising=False)
    else:
        monkeypatch.setenv("KLUG_SESSION_SECRET", secret)

    monkeypatch.setenv("KLUG_API_AUTH_MODE", auth_mode)
    get_settings.cache_clear()


def test_session_login_and_me(monkeypatch) -> None:
    _set_session_env(
        monkeypatch,
        password="session-pass",
        secret="session-secret",
    )

    client = TestClient(app)
    login = client.post("/api/v1/session/login", json={"password": "session-pass"})

    assert login.status_code == 200
    me = client.get("/api/v1/session/me")
    assert me.status_code == 200
    assert me.json()["authenticated"] is True


def test_session_login_wrong_password(monkeypatch) -> None:
    _set_session_env(
        monkeypatch,
        password="session-pass",
        secret="session-secret",
    )

    client = TestClient(app)
    login = client.post("/api/v1/session/login", json={"password": "wrong"})
    assert login.status_code == 401


def test_session_login_not_configured(monkeypatch) -> None:
    _set_session_env(
        monkeypatch,
        password=None,
        secret=None,
    )

    client = TestClient(app)
    login = client.post("/api/v1/session/login", json={"password": "any"})
    assert login.status_code == 503


def test_session_logout_clears_session(monkeypatch) -> None:
    _set_session_env(
        monkeypatch,
        password="session-pass",
        secret="session-secret",
    )

    client = TestClient(app)
    login = client.post("/api/v1/session/login", json={"password": "session-pass"})
    assert login.status_code == 200

    logout = client.delete("/api/v1/session/logout")
    assert logout.status_code == 200

    me = client.get("/api/v1/session/me")
    assert me.status_code == 200
    assert me.json()["authenticated"] is False
