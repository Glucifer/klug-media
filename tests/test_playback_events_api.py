from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.playback_events import PlaybackEventService


class DummyPlaybackEvent:
    def __init__(self) -> None:
        self.playback_event_id = uuid4()
        self.collector = "node_red"
        self.playback_source = "kodi"
        self.event_type = "stop"
        self.user_id = uuid4()
        self.occurred_at = datetime.now(UTC)
        self.source_event_id = "evt-1"
        self.session_key = "session-1"
        self.media_type = "movie"
        self.title = "The Matrix"
        self.year = 1999
        self.season_number = None
        self.episode_number = None
        self.tmdb_id = 603
        self.imdb_id = "tt0133093"
        self.tvdb_id = None
        self.progress_percent = Decimal("95.00")
        self.payload = {"state": "stopped"}
        self.created_at = datetime.now(UTC)


def test_list_playback_events_returns_items(monkeypatch) -> None:
    event = DummyPlaybackEvent()
    called: dict[str, object] = {}

    def fake_list_playback_events(_session, **kwargs):
        called.update(kwargs)
        return [event]

    monkeypatch.setattr(
        PlaybackEventService,
        "list_playback_events",
        fake_list_playback_events,
    )

    client = TestClient(app)
    response = client.get("/api/v1/playback-events")

    assert response.status_code == 200
    assert called["limit"] == 50
    assert called["offset"] == 0
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["playback_source"] == "kodi"
    assert payload[0]["payload"]["state"] == "stopped"


def test_list_playback_events_forwards_filters(monkeypatch) -> None:
    event = DummyPlaybackEvent()
    called: dict[str, object] = {}

    def fake_list_playback_events(_session, **kwargs):
        called.update(kwargs)
        return [event]

    monkeypatch.setattr(
        PlaybackEventService,
        "list_playback_events",
        fake_list_playback_events,
    )

    client = TestClient(app)
    response = client.get(
        f"/api/v1/playback-events?user_id={event.user_id}&playback_source=kodi&collector=node_red&session_key=session-1&event_type=stop&media_type=movie&limit=10&offset=5"
    )

    assert response.status_code == 200
    assert called["user_id"] == event.user_id
    assert called["playback_source"] == "kodi"
    assert called["collector"] == "node_red"
    assert called["session_key"] == "session-1"
    assert called["event_type"] == "stop"
    assert called["media_type"] == "movie"
    assert called["limit"] == 10
    assert called["offset"] == 5


def test_list_playback_events_invalid_media_type_returns_422() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/playback-events?media_type=bad")
    assert response.status_code == 422
