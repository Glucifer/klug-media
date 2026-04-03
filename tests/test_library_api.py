from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.library import LibraryService


def test_list_library_movies_returns_rows(monkeypatch) -> None:
    media_item_id = uuid4()

    def fake_list_movies(_session, **kwargs):
        assert kwargs["query"] == "alien"
        assert kwargs["year"] == 1979
        return [
            {
                "media_item_id": media_item_id,
                "title": "Alien",
                "year": 1979,
                "watch_count": 2,
                "latest_watched_at": datetime.now(UTC),
                "latest_rating_value": 9,
                "latest_rating_scale": "10-star",
                "enrichment_status": "enriched",
                "horrorfest_year": 2025,
            }
        ]

    monkeypatch.setattr(LibraryService, "list_movies", fake_list_movies)

    client = TestClient(app)
    response = client.get("/api/v1/library/movies?query=alien&year=1979")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["title"] == "Alien"
    assert payload[0]["watch_count"] == 2


def test_list_library_episodes_returns_rows(monkeypatch) -> None:
    media_item_id = uuid4()
    show_id = uuid4()

    monkeypatch.setattr(
        LibraryService,
        "list_episodes",
        lambda _session, **kwargs: [
            {
                "media_item_id": media_item_id,
                "show_id": show_id,
                "show_title": "The X-Files",
                "season_number": 1,
                "episode_number": 1,
                "title": "Pilot",
                "watch_count": 1,
                "latest_watched_at": datetime.now(UTC),
                "enrichment_status": "enriched",
                "horrorfest_year": None,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/library/episodes?show_query=x-files")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["show_title"] == "The X-Files"
    assert payload[0]["episode_number"] == 1


def test_list_library_shows_returns_rows(monkeypatch) -> None:
    show_id = uuid4()
    media_item_id = uuid4()

    monkeypatch.setattr(
        LibraryService,
        "list_shows",
        lambda _session, **kwargs: [
            {
                "show_id": show_id,
                "media_item_id": media_item_id,
                "title": "Severance",
                "year": 2022,
                "watched_episodes": 10,
                "total_episodes": 19,
                "watched_percent": Decimal("52.63"),
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/library/shows?query=sev")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["title"] == "Severance"
    assert payload[0]["watched_percent"] == "52.63"
