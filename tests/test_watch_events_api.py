from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.watch_events import WatchEventConstraintError, WatchEventService


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
        self.completed = True
        self.rating_value = Decimal("4.50")
        self.rating_scale = "5-star"
        self.media_version_id = None
        self.import_batch_id = None
        self.created_at = datetime.now(UTC)
        self.rewatch = False
        self.dedupe_hash = "abc123"
        self.created_by = None
        self.source_event_id = "evt-1"


def test_list_watch_events_returns_items(monkeypatch) -> None:
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
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["playback_source"] == "jellyfin"


def test_list_watch_events_forwards_filters(monkeypatch) -> None:
    event = DummyWatchEvent()
    called: dict[str, object] = {}

    def fake_list_watch_events(_session, **_kwargs):
        called.update(_kwargs)
        return [event]

    monkeypatch.setattr(WatchEventService, "list_watch_events", fake_list_watch_events)

    client = TestClient(app)
    response = client.get(
        f"/api/v1/watch-events?user_id={event.user_id}&media_type=episode&limit=10&offset=5"
    )

    assert response.status_code == 200
    assert called["user_id"] == event.user_id
    assert called["media_type"] == "episode"
    assert called["limit"] == 10
    assert called["offset"] == 5


def test_list_watch_events_invalid_media_type_returns_422() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/watch-events?media_type=bad")
    assert response.status_code == 422


def test_list_watch_events_returns_enriched_media_fields(monkeypatch) -> None:
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
                "created_at": datetime.now(UTC),
                "rewatch": False,
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


def test_create_watch_event_returns_201(monkeypatch) -> None:
    event = DummyWatchEvent()

    def fake_create_watch_event(_session, **kwargs):
        assert kwargs["playback_source"] == "jellyfin"
        return event

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


def test_create_watch_event_constraint_error_returns_409(monkeypatch) -> None:
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
