from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.webhooks import PlaybackIngestResult
from app.services.webhooks import WebhookService


def _set_auth(
    monkeypatch,
    *,
    api_key: str | None,
    auth_mode: str | None = None,
    app_env: str | None = None,
) -> None:
    if api_key is None:
        monkeypatch.delenv("KLUG_API_KEY", raising=False)
    else:
        monkeypatch.setenv("KLUG_API_KEY", api_key)
    if auth_mode is None:
        monkeypatch.delenv("KLUG_API_AUTH_MODE", raising=False)
    else:
        monkeypatch.setenv("KLUG_API_AUTH_MODE", auth_mode)
    if app_env is None:
        monkeypatch.delenv("APP_ENV", raising=False)
    else:
        monkeypatch.setenv("APP_ENV", app_env)
    get_settings.cache_clear()


def test_kodi_webhook_requires_auth(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key="secret-key", auth_mode="write", app_env="prod")
    client = TestClient(app)
    response = client.post(
        "/api/v1/webhooks/kodi/scrobble",
        json={
            "user_id": str(uuid4()),
            "media_type": "movie",
            "title": "The Matrix",
        },
    )

    assert response.status_code == 401


def test_kodi_movie_scrobble(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key=None, auth_mode="write", app_env="dev")
    user_id = str(uuid4())
    mock_watch_event = MagicMock()
    mock_watch_event.watch_id = uuid4()
    mock_watch_event.user_id = uuid4()
    mock_watch_event.media_item_id = uuid4()
    mock_watch_event.watched_at = "2026-01-01T00:00:00Z"
    mock_watch_event.playback_source = "Kodi Node-Red"
    mock_watch_event.total_seconds = None
    mock_watch_event.watched_seconds = None
    mock_watch_event.progress_percent = 100.0
    mock_watch_event.completed = True
    mock_watch_event.rating_value = None
    mock_watch_event.rating_scale = None
    mock_watch_event.media_version_id = None
    mock_watch_event.import_batch_id = None
    mock_watch_event.origin_kind = "live_playback"
    mock_watch_event.origin_playback_event_id = uuid4()
    mock_watch_event.created_at = "2026-01-01T00:00:00Z"
    mock_watch_event.rewatch = False
    mock_watch_event.dedupe_hash = None
    mock_watch_event.created_by = None
    mock_watch_event.source_event_id = None

    called = False

    def fake_process(*args, **kwargs):
        nonlocal called
        called = True
        return mock_watch_event

    monkeypatch.setattr(WebhookService, "process_kodi_scrobble", fake_process)

    client = TestClient(app)
    response = client.post(
        "/api/v1/webhooks/kodi/scrobble",
        json={
            "user_id": user_id,
            "media_type": "movie",
            "title": "The Matrix",
            "year": 1999,
            "tmdb_id": 603,
            "progress_percent": 100.0,
            "playback_source": "Kodi Node-Red",
        },
    )

    assert response.status_code == 201
    assert called is True
    data = response.json()
    assert data["playback_source"] == "Kodi Node-Red"


def test_kodi_event_endpoint_records_without_watch_event(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key=None, auth_mode="write", app_env="dev")
    playback_event = MagicMock()
    playback_event.playback_event_id = uuid4()
    playback_event.collector = "node_red"
    playback_event.playback_source = "kodi"
    playback_event.event_type = "pause"
    playback_event.user_id = uuid4()
    playback_event.occurred_at = "2026-01-01T00:00:00Z"
    playback_event.source_event_id = "evt-1"
    playback_event.session_key = "session-1"
    playback_event.media_type = "movie"
    playback_event.title = "The Matrix"
    playback_event.year = 1999
    playback_event.season_number = None
    playback_event.episode_number = None
    playback_event.tmdb_id = 603
    playback_event.imdb_id = None
    playback_event.tvdb_id = None
    playback_event.total_seconds = 7200
    playback_event.watched_seconds = 3060
    playback_event.progress_percent = 42.5
    playback_event.payload = {"player_state": "paused"}
    playback_event.decision_status = "recorded_only"
    playback_event.decision_reason = "Event recorded for later scrobble evaluation"
    playback_event.watch_id = None
    playback_event.created_at = "2026-01-01T00:00:01Z"

    def fake_ingest(*args, **kwargs):
        return PlaybackIngestResult(
            action="recorded_only",
            reason="Event recorded for later scrobble evaluation",
            playback_event=playback_event,
        )

    monkeypatch.setattr(WebhookService, "ingest_kodi_playback_event", fake_ingest)

    client = TestClient(app)
    response = client.post(
        "/api/v1/webhooks/kodi/events",
        json={
            "user_id": str(uuid4()),
            "event_type": "pause",
            "occurred_at": "2026-01-01T00:00:00Z",
            "source_event_id": "evt-1",
            "session_key": "session-1",
            "media_type": "movie",
            "title": "The Matrix",
            "year": 1999,
            "tmdb_id": 603,
            "total_seconds": 7200,
            "watched_seconds": 3060,
            "progress_percent": 42.5,
            "payload": {"player_state": "paused"},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["action"] == "recorded_only"
    assert data["watch_event"] is None
    assert data["playback_event"]["event_type"] == "pause"


def test_kodi_episode_missing_show_metadata(monkeypatch) -> None:
    _set_auth(monkeypatch, api_key=None, auth_mode="write", app_env="dev")
    user_id = str(uuid4())
    client = TestClient(app)
    
    def fake_process(*args, **kwargs):
        raise ValueError("Episode scrobble requires show title or tmdb_id/tvdb_id")

    monkeypatch.setattr(WebhookService, "process_kodi_scrobble", fake_process)

    response = client.post(
        "/api/v1/webhooks/kodi/scrobble",
        json={
            "user_id": user_id,
            "media_type": "episode",
            "title": "Unknown TV Show",
        },
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "require" in data["detail"].lower()
