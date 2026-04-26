import pytest

from app.core.config import get_settings


@pytest.fixture(autouse=True)
def clear_auth_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("KLUG_API_KEY", "")
    monkeypatch.setenv("KLUG_API_AUTH_MODE", "write")
    monkeypatch.setenv("KLUG_SESSION_PASSWORD", "")
    monkeypatch.setenv("KLUG_SESSION_SECRET", "")
    monkeypatch.delenv("KLUG_SESSION_TTL_SECONDS", raising=False)
    monkeypatch.delenv("KLUG_IMPORT_UPLOAD_MAX_MB", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
