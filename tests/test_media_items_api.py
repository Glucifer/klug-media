from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.media_items import MediaItemAlreadyExistsError, MediaItemService


class DummyMediaItem:
    def __init__(self, *, media_type: str, title: str) -> None:
        self.media_item_id = uuid4()
        self.type = media_type
        self.title = title
        self.year = 2025
        self.summary = None
        self.poster_url = None
        self.release_date = None
        self.tmdb_id = 100
        self.imdb_id = "tt1234567"
        self.tvdb_id = None
        self.show_tmdb_id = None
        self.season_number = None
        self.episode_number = None
        self.metadata_source = None
        self.metadata_updated_at = None
        self.base_runtime_seconds = None
        self.enrichment_status = "pending"
        self.enrichment_error = None
        self.enrichment_attempted_at = None
        self.created_at = datetime.now(UTC)


def _set_permissive_auth(monkeypatch) -> None:
    monkeypatch.setenv("KLUG_API_KEY", "")
    monkeypatch.setenv("KLUG_API_AUTH_MODE", "write")
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("KLUG_SESSION_PASSWORD", "")
    monkeypatch.setenv("KLUG_SESSION_SECRET", "")
    get_settings.cache_clear()


def test_list_media_items_returns_items(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    expected_item = DummyMediaItem(media_type="movie", title="Alien")

    def fake_list_media_items(_session):
        return [expected_item]

    monkeypatch.setattr(MediaItemService, "list_media_items", fake_list_media_items)

    client = TestClient(app)
    response = client.get("/api/v1/media-items")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Alien"


def test_create_media_item_returns_201(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    created_item = DummyMediaItem(media_type="movie", title="The Thing")

    def fake_create_media_item(_session, **kwargs):
        assert kwargs["media_type"] == "movie"
        assert kwargs["title"] == "The Thing"
        return created_item

    monkeypatch.setattr(MediaItemService, "create_media_item", fake_create_media_item)

    client = TestClient(app)
    response = client.post(
        "/api/v1/media-items",
        json={"type": "movie", "title": "The Thing", "year": 1982},
    )

    assert response.status_code == 201
    assert response.json()["type"] == "movie"
    assert response.json()["title"] == "The Thing"


def test_create_media_item_duplicate_returns_409(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    def fake_create_media_item(_session, **_kwargs):
        raise MediaItemAlreadyExistsError("Duplicate media reference")

    monkeypatch.setattr(MediaItemService, "create_media_item", fake_create_media_item)

    client = TestClient(app)
    response = client.post(
        "/api/v1/media-items",
        json={"type": "movie", "title": "Alien"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate media reference"
