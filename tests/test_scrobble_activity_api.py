from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.scrobble_activity import ScrobbleActivityService


class DummyScrobbleActivityRow:
    def __init__(self) -> None:
        self.playback_event_id = uuid4()
        self.occurred_at = datetime.now(UTC)
        self.user_id = uuid4()
        self.username = "travis"
        self.collector = "node_red"
        self.playback_source = "kodi"
        self.event_type = "stop"
        self.media_type = "episode"
        self.guessed_title = "FROM"
        self.year = 2025
        self.season_number = 3
        self.episode_number = 10
        self.tmdb_id = None
        self.imdb_id = None
        self.tvdb_id = 10706489
        self.progress_percent = Decimal("99.57")
        self.decision_status = "watch_event_created"
        self.decision_reason = None
        self.watch_id = uuid4()
        self.media_item_id = uuid4()
        self.origin_kind = "live_playback"
        self.matched_title = "FROM"
        self.matched_media_type = "episode"
        self.result_label = "created"
        self.is_unmatched = False


def test_list_scrobble_activity_returns_items(monkeypatch) -> None:
    row = DummyScrobbleActivityRow()
    called: dict[str, object] = {}

    def fake_list_scrobble_activity(_session, **kwargs):
        called.update(kwargs)
        return [row]

    monkeypatch.setattr(
        ScrobbleActivityService, "list_scrobble_activity", fake_list_scrobble_activity
    )

    client = TestClient(app)
    response = client.get("/api/v1/scrobble-activity")

    assert response.status_code == 200
    assert called["limit"] == 50
    assert called["offset"] == 0
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["playback_source"] == "kodi"
    assert payload[0]["origin_kind"] == "live_playback"
    assert payload[0]["result_label"] == "created"


def test_list_scrobble_activity_forwards_filters(monkeypatch) -> None:
    row = DummyScrobbleActivityRow()
    called: dict[str, object] = {}

    def fake_list_scrobble_activity(_session, **kwargs):
        called.update(kwargs)
        return [row]

    monkeypatch.setattr(
        ScrobbleActivityService, "list_scrobble_activity", fake_list_scrobble_activity
    )

    client = TestClient(app)
    response = client.get(
        f"/api/v1/scrobble-activity?user_id={row.user_id}&collector=node_red&playback_source=kodi&decision_status=watch_event_created&event_type=stop&media_type=episode&only_unmatched=true&limit=10&offset=5"
    )

    assert response.status_code == 200
    assert called["user_id"] == row.user_id
    assert called["collector"] == "node_red"
    assert called["playback_source"] == "kodi"
    assert called["decision_status"] == "watch_event_created"
    assert called["event_type"] == "stop"
    assert called["media_type"] == "episode"
    assert called["only_unmatched"] is True
    assert called["limit"] == 10
    assert called["offset"] == 5


def test_list_scrobble_activity_invalid_media_type_returns_422() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/scrobble-activity?media_type=bad")
    assert response.status_code == 422
