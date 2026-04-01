from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.watch_events import WatchEventConstraintError, WatchEventService
from app.services.watch_events import WatchEventCreateResult


class DummyWatchEvent:
    def __init__(self) -> None:
        self.watch_id = uuid4()
        self.user_id = uuid4()
        self.media_item_id = uuid4()
        self.watched_at = datetime.now(UTC)
        self.playback_source = "jellyfin"
        self.total_seconds = 7200
        self.watched_seconds = 7200
        self.progress_percent = Decimal("100.00")
        self.watch_version_name = None
        self.watch_runtime_seconds = None
        self.effective_runtime_seconds = 7200
        self.completed = True
        self.rating_value = Decimal("4.50")
        self.rating_scale = "5-star"
        self.media_version_id = None
        self.import_batch_id = None
        self.origin_kind = "manual_entry"
        self.origin_playback_event_id = None
        self.created_at = datetime.now(UTC)
        self.updated_at = None
        self.updated_by = None
        self.update_reason = None
        self.rewatch = False
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.deleted_reason = None
        self.dedupe_hash = "abc123"
        self.created_by = None
        self.source_event_id = "evt-1"
        self.horrorfest_year = None
        self.horrorfest_watch_order = None
        self.is_horrorfest_watch = False


def _set_permissive_auth(monkeypatch) -> None:
    monkeypatch.setenv("KLUG_API_KEY", "")
    monkeypatch.setenv("KLUG_API_AUTH_MODE", "write")
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("KLUG_SESSION_PASSWORD", "")
    monkeypatch.setenv("KLUG_SESSION_SECRET", "")
    get_settings.cache_clear()


def test_list_watch_events_returns_items(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()
    called: dict[str, object] = {}

    def fake_list_watch_events(_session, **_kwargs):
        called.update(_kwargs)
        return [event]

    monkeypatch.setattr(WatchEventService, "list_watch_events", fake_list_watch_events)

    client = TestClient(app)
    response = client.get("/api/v1/watch-events")

    assert response.status_code == 200
    assert called["offset"] == 0
    assert called["media_type"] is None
    assert called["include_deleted"] is False
    assert called["deleted_only"] is False
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["playback_source"] == "jellyfin"


def test_list_watch_events_forwards_filters(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()
    called: dict[str, object] = {}

    def fake_list_watch_events(_session, **_kwargs):
        called.update(_kwargs)
        return [event]

    monkeypatch.setattr(WatchEventService, "list_watch_events", fake_list_watch_events)

    client = TestClient(app)
    response = client.get(
        f"/api/v1/watch-events?user_id={event.user_id}&media_type=episode&limit=10&offset=5&local_date_from=2026-01-01&local_date_to=2026-01-02"
    )

    assert response.status_code == 200
    assert called["user_id"] == event.user_id
    assert called["media_type"] == "episode"
    assert str(called["local_date_from"]) == "2026-01-01"
    assert str(called["local_date_to"]) == "2026-01-02"
    assert called["include_deleted"] is False
    assert called["limit"] == 10
    assert called["offset"] == 5


def test_list_watch_events_forwards_include_deleted(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()
    called: dict[str, object] = {}

    def fake_list_watch_events(_session, **_kwargs):
        called.update(_kwargs)
        return [event]

    monkeypatch.setattr(WatchEventService, "list_watch_events", fake_list_watch_events)

    client = TestClient(app)
    response = client.get("/api/v1/watch-events?include_deleted=true")

    assert response.status_code == 200
    assert called["include_deleted"] is True


def test_list_watch_events_invalid_media_type_returns_422() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/watch-events?media_type=bad")
    assert response.status_code == 422


def test_list_unrated_watch_events_returns_items(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()
    event.rating_value = None
    event.rating_scale = None
    called: dict[str, object] = {}

    def fake_list_unrated_watch_events(_session, **kwargs):
        called.update(kwargs)
        return [event]

    monkeypatch.setattr(
        WatchEventService,
        "list_unrated_watch_events",
        fake_list_unrated_watch_events,
    )

    client = TestClient(app)
    response = client.get("/api/v1/watch-events/unrated?limit=10")

    assert response.status_code == 200
    assert called["limit"] == 10
    assert response.json()[0]["rating_value"] is None


def test_list_watch_events_returns_enriched_media_fields(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    watch_id = uuid4()
    user_id = uuid4()
    media_item_id = uuid4()

    def fake_list_watch_events(_session, **_kwargs):
        return [
            {
                "watch_id": watch_id,
                "user_id": user_id,
                "media_item_id": media_item_id,
                "watched_at": datetime.now(UTC),
                "playback_source": "legacy_backup",
                "total_seconds": None,
                "watched_seconds": None,
                "progress_percent": None,
                "completed": True,
                "rating_value": None,
                "rating_scale": None,
                "media_version_id": None,
                "import_batch_id": None,
                "origin_kind": "manual_import",
                "origin_playback_event_id": None,
                "created_at": datetime.now(UTC),
                "updated_at": None,
                "updated_by": None,
                "update_reason": None,
                "rewatch": False,
                "is_deleted": False,
                "deleted_at": None,
                "deleted_by": None,
                "deleted_reason": None,
                "dedupe_hash": None,
                "created_by": None,
                "source_event_id": "evt-9",
                "media_item_title": "The Nest",
                "media_item_type": "episode",
                "media_item_season_number": 1,
                "media_item_episode_number": 8,
                "display_title": "Scavengers Reign S01E08",
            }
        ]

    monkeypatch.setattr(WatchEventService, "list_watch_events", fake_list_watch_events)

    client = TestClient(app)
    response = client.get("/api/v1/watch-events")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["media_item_title"] == "The Nest"
    assert payload[0]["media_item_type"] == "episode"
    assert payload[0]["media_item_season_number"] == 1
    assert payload[0]["media_item_episode_number"] == 8
    assert payload[0]["display_title"] == "Scavengers Reign S01E08"


def test_list_watch_events_rejects_invalid_local_date() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/watch-events?local_date_from=not-a-date")
    assert response.status_code == 422


def test_create_watch_event_returns_201(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()

    def fake_create_watch_event(_session, **kwargs):
        assert kwargs["playback_source"] == "jellyfin"
        return WatchEventCreateResult(watch_event=event, created=True)

    monkeypatch.setattr(
        WatchEventService, "create_watch_event", fake_create_watch_event
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/watch-events",
        json={
            "user_id": str(event.user_id),
            "media_item_id": str(event.media_item_id),
            "watched_at": event.watched_at.isoformat(),
            "playback_source": "jellyfin",
            "completed": True,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["playback_source"] == "jellyfin"
    assert payload["watched_at"].endswith("Z")
    assert payload["created_at"].endswith("Z")


def test_create_watch_event_rejects_naive_watched_at() -> None:
    monkeypatch = pytest.MonkeyPatch()
    _set_permissive_auth(monkeypatch)
    client = TestClient(app)
    response = client.post(
        "/api/v1/watch-events",
        json={
            "user_id": str(uuid4()),
            "media_item_id": str(uuid4()),
            "watched_at": "2026-01-01T12:00:00",
            "playback_source": "jellyfin",
            "completed": True,
        },
    )

    assert response.status_code == 422
    monkeypatch.undo()


def test_create_manual_watch_event_returns_201(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()

    def fake_create_manual_watch_event(_session, **kwargs):
        assert kwargs["media_type"] == "movie"
        assert kwargs["tmdb_id"] == 1091
        return WatchEventCreateResult(watch_event=event, created=True)

    monkeypatch.setattr(
        WatchEventService, "create_manual_watch_event", fake_create_manual_watch_event
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/watch-events/manual",
        json={
            "user_id": str(event.user_id),
            "watched_at": event.watched_at.isoformat(),
            "playback_source": "blu_ray",
            "media_type": "movie",
            "tmdb_id": 1091,
            "completed": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["watch_id"] == str(event.watch_id)


def test_create_manual_watch_event_rejects_episode_without_show_tmdb_id(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    client = TestClient(app)
    response = client.post(
        "/api/v1/watch-events/manual",
        json={
            "user_id": str(uuid4()),
            "watched_at": datetime.now(UTC).isoformat(),
            "playback_source": "streaming",
            "media_type": "episode",
            "tmdb_episode_id": 12345,
            "season_number": 1,
            "episode_number": 1,
            "completed": True,
        },
    )

    assert response.status_code == 422
    assert "show_tmdb_id" in response.json()["detail"][0]["msg"]


def test_create_watch_event_constraint_error_returns_409(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()

    def fake_create_watch_event(_session, **_kwargs):
        raise WatchEventConstraintError("Watch event failed database constraints")

    monkeypatch.setattr(
        WatchEventService, "create_watch_event", fake_create_watch_event
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/watch-events",
        json={
            "user_id": str(event.user_id),
            "media_item_id": str(event.media_item_id),
            "watched_at": event.watched_at.isoformat(),
            "playback_source": "jellyfin",
            "completed": True,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Watch event failed database constraints"


def test_delete_watch_event_returns_updated_row(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()
    event.is_deleted = True
    event.deleted_by = "operator"
    event.deleted_reason = "duplicate"

    monkeypatch.setattr(
        WatchEventService,
        "soft_delete_watch_event",
        lambda *_args, **_kwargs: event,
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/watch-events/{event.watch_id}/delete",
        json={"updated_by": "operator", "update_reason": "duplicate"},
    )

    assert response.status_code == 200
    assert response.json()["is_deleted"] is True


def test_restore_watch_event_returns_updated_row(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()

    monkeypatch.setattr(
        WatchEventService,
        "restore_watch_event",
        lambda *_args, **_kwargs: event,
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/watch-events/{event.watch_id}/restore",
        json={"updated_by": "operator", "update_reason": "restored"},
    )

    assert response.status_code == 200
    assert response.json()["is_deleted"] is False


def test_correct_watch_event_returns_updated_row(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()
    event.updated_by = "operator"
    event.update_reason = "timezone fix"

    monkeypatch.setattr(
        WatchEventService,
        "correct_watch_event",
        lambda *_args, **_kwargs: event,
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/watch-events/{event.watch_id}/correct",
        json={
            "updated_by": "operator",
            "update_reason": "timezone fix",
            "completed": True,
            "rewatch": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["updated_by"] == "operator"
    assert payload["update_reason"] == "timezone fix"


def test_rate_watch_event_returns_updated_row(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()
    event.rating_value = Decimal("8")
    event.rating_scale = "10-star"
    event.updated_by = "operator"
    event.update_reason = "rated from queue"

    monkeypatch.setattr(
        WatchEventService,
        "rate_watch_event",
        lambda *_args, **_kwargs: event,
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/watch-events/{event.watch_id}/rate",
        json={
            "updated_by": "operator",
            "update_reason": "rated from queue",
            "rating_value": 8,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rating_value"] == "8"
    assert payload["rating_scale"] == "10-star"


def test_set_watch_event_version_override_returns_updated_row(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    event = DummyWatchEvent()
    event.watch_version_name = "Director's Cut"
    event.watch_runtime_seconds = 7920
    event.effective_runtime_seconds = 7920
    event.updated_by = "operator"
    event.update_reason = "manual cut selection"

    monkeypatch.setattr(
        WatchEventService,
        "set_watch_event_version_override",
        lambda *_args, **_kwargs: event,
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/watch-events/{event.watch_id}/version",
        json={
            "updated_by": "operator",
            "update_reason": "manual cut selection",
            "version_name": "Director's Cut",
            "runtime_minutes": 132,
            "clear_override": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["watch_version_name"] == "Director's Cut"
    assert payload["watch_runtime_seconds"] == 7920
