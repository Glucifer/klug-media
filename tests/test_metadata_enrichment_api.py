from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.media_enrichment import MediaEnrichmentService


class DummyEnrichmentItem:
    def __init__(self) -> None:
        self.media_item_id = uuid4()
        self.type = "movie"
        self.title = "Alien"
        self.year = 1979
        self.summary = "In space, no one can hear you scream."
        self.poster_url = "https://image.tmdb.org/t/p/w500/poster.jpg"
        self.release_date = None
        self.tmdb_id = 348
        self.imdb_id = "tt0078748"
        self.tvdb_id = None
        self.show_tmdb_id = None
        self.season_number = None
        self.episode_number = None
        self.metadata_source = "tmdb"
        self.metadata_updated_at = datetime.now(UTC)
        self.base_runtime_seconds = 7020
        self.enrichment_status = "enriched"
        self.enrichment_error = None
        self.enrichment_attempted_at = datetime.now(UTC)
        self.created_at = datetime.now(UTC)


def _set_permissive_auth(monkeypatch) -> None:
    monkeypatch.setenv("KLUG_API_KEY", "")
    monkeypatch.setenv("KLUG_API_AUTH_MODE", "write")
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("KLUG_SESSION_PASSWORD", "")
    monkeypatch.setenv("KLUG_SESSION_SECRET", "")
    get_settings.cache_clear()


def test_list_metadata_enrichment_items_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    item = DummyEnrichmentItem()
    called: dict[str, object] = {}

    def fake_list_queue(_session, **kwargs):
        called.update(kwargs)
        return [item]

    monkeypatch.setattr(MediaEnrichmentService, "list_queue", fake_list_queue)

    client = TestClient(app)
    response = client.get("/api/v1/metadata-enrichment/items?enrichment_status=pending&limit=10")

    assert response.status_code == 200
    assert called["enrichment_status"] == "pending"
    assert called["limit"] == 10
    assert response.json()[0]["title"] == "Alien"
    assert response.json()[0]["last_lookup_kind"] == "movie_details"


def test_process_pending_metadata_items_returns_batch(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    item = DummyEnrichmentItem()

    def fake_process_pending(_session, *, limit):
        assert limit == 5
        return [type("Result", (), {"media_item": item, "action": "enriched"})()]

    monkeypatch.setattr(
        MediaEnrichmentService,
        "process_pending_items",
        fake_process_pending,
    )
    monkeypatch.setattr(MediaEnrichmentService, "count_pending_items", lambda *_args, **_kwargs: 12)

    client = TestClient(app)
    response = client.post("/api/v1/metadata-enrichment/process-pending?limit=5")

    assert response.status_code == 200
    payload = response.json()
    assert payload["processed_count"] == 1
    assert payload["enriched_count"] == 1
    assert payload["failed_count"] == 0
    assert payload["skipped_count"] == 0
    assert payload["remaining_pending_count"] == 12
    assert payload["items"][0]["tmdb_id"] == 348
    assert payload["items"][0]["next_action"] is None


def test_retry_metadata_enrichment_returns_not_found(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    def fake_retry(_session, *, media_item_id):
        raise ValueError(f"Media item '{media_item_id}' not found")

    monkeypatch.setattr(MediaEnrichmentService, "retry_media_item", fake_retry)

    client = TestClient(app)
    response = client.post(f"/api/v1/metadata-enrichment/items/{uuid4()}/retry")

    assert response.status_code == 404


def test_list_metadata_enrichment_items_include_failure_guidance(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    item = DummyEnrichmentItem()
    item.enrichment_status = "failed"
    item.enrichment_error = "tmdb_no_match"
    item.tmdb_id = None

    monkeypatch.setattr(MediaEnrichmentService, "list_queue", lambda *_args, **_kwargs: [item])

    client = TestClient(app)
    response = client.get("/api/v1/metadata-enrichment/items?enrichment_status=failed")

    assert response.status_code == 200
    payload = response.json()[0]
    assert payload["failure_code"] == "tmdb_no_match"
    assert payload["next_action"] == "Review source IDs and retry manually"
