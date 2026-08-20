from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.jellyfin_webhooks import (
    JellyfinWebhookIngestResult,
    JellyfinWebhookService,
)


def _payload() -> dict:
    return {
        "notification_type": "PlaybackStop",
        "server_id": "server-1",
        "occurred_at": "2026-08-20T12:00:00Z",
        "jellyfin_user_id": "11111111-1111-1111-1111-111111111111",
        "item_id": "22222222222222222222222222222222",
        "item_type": "Movie",
        "title": "Alien",
        "runtime_ticks": 70_200_000_000,
        "playback_position_ticks": 68_800_000_000,
        "played_to_completion": True,
    }


def _playback_event():
    return SimpleNamespace(
        playback_event_id=uuid4(),
        collector="jellyfin_webhook",
        playback_source="jellyfin",
        event_type="stop",
        user_id=uuid4(),
        occurred_at=datetime(2026, 8, 20, 12, tzinfo=UTC),
        source_event_id="jellyfin:abc",
        session_key=None,
        media_type="movie",
        title="Alien",
        year=1979,
        season_number=None,
        episode_number=None,
        tmdb_id=348,
        imdb_id=None,
        tvdb_id=None,
        total_seconds=7020,
        watched_seconds=6880,
        progress_percent=98.01,
        payload={},
        decision_status="recorded_only",
        decision_reason="test",
        watch_id=None,
        created_at=datetime(2026, 8, 20, 12, tzinfo=UTC),
    )


def test_jellyfin_webhook_requires_auth(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("KLUG_API_AUTH_MODE", "write")
    monkeypatch.setenv("KLUG_API_KEY", "secret")
    get_settings.cache_clear()

    response = TestClient(app).post(
        "/api/v1/webhooks/jellyfin/events",
        json=_payload(),
    )

    assert response.status_code == 401


def test_jellyfin_webhook_returns_ingest_decision(monkeypatch) -> None:
    event = _playback_event()
    monkeypatch.setattr(
        JellyfinWebhookService,
        "ingest",
        lambda *_args, **_kwargs: JellyfinWebhookIngestResult(
            action="recorded_only",
            playback_event=event,
            reason="test",
        ),
    )

    response = TestClient(app).post(
        "/api/v1/webhooks/jellyfin/events",
        json=_payload(),
    )

    assert response.status_code == 201
    assert response.json()["action"] == "recorded_only"
    assert response.json()["playback_event"]["collector"] == "jellyfin_webhook"


def test_jellyfin_webhook_rejects_unmapped_user(monkeypatch) -> None:
    def reject(*_args, **_kwargs):
        raise ValueError("Jellyfin user is not mapped to Klug")

    monkeypatch.setattr(JellyfinWebhookService, "ingest", reject)

    response = TestClient(app).post(
        "/api/v1/webhooks/jellyfin/events",
        json=_payload(),
    )

    assert response.status_code == 422
    assert "not mapped" in response.json()["detail"]
