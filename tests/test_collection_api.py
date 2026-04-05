from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.collection import CollectionService


def test_list_collection_movies_returns_rows(monkeypatch) -> None:
    collection_entry_id = uuid4()
    media_item_id = uuid4()

    monkeypatch.setattr(
        CollectionService,
        "list_movies",
        lambda _session, **kwargs: [
            {
                "collection_entry_id": collection_entry_id,
                "source": "jellyfin",
                "source_item_id": "jf-movie-1",
                "media_item_id": media_item_id,
                "title": "Alien",
                "year": 1979,
                "tmdb_id": 348,
                "imdb_id": "tt0078748",
                "tvdb_id": None,
                "is_present": True,
                "first_seen_at": datetime.now(UTC),
                "last_seen_at": datetime.now(UTC),
                "missing_since": None,
                "library_id": "movies",
                "library_name": "Movies",
                "added_at": datetime.now(UTC),
                "runtime_seconds": 7020,
                "file_path": "D:/media/movies/Alien.mkv",
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/collection/movies?query=alien&present=true")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["title"] == "Alien"
    assert payload[0]["source_item_id"] == "jf-movie-1"


def test_list_collection_shows_returns_rows(monkeypatch) -> None:
    collection_entry_id = uuid4()
    show_id = uuid4()

    monkeypatch.setattr(
        CollectionService,
        "list_shows",
        lambda _session, **kwargs: [
            {
                "collection_entry_id": collection_entry_id,
                "source": "jellyfin",
                "source_item_id": "jf-show-1",
                "show_id": show_id,
                "title": "Severance",
                "year": 2022,
                "tmdb_id": None,
                "imdb_id": None,
                "tvdb_id": None,
                "is_present": False,
                "first_seen_at": datetime.now(UTC),
                "last_seen_at": datetime.now(UTC),
                "missing_since": datetime.now(UTC),
                "library_id": "tv",
                "library_name": "TV Shows",
                "added_at": None,
                "runtime_seconds": None,
                "file_path": None,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/collection/shows?present=false")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["title"] == "Severance"
    assert payload[0]["tmdb_id"] is None


def test_list_collection_episodes_returns_rows(monkeypatch) -> None:
    collection_entry_id = uuid4()
    media_item_id = uuid4()
    show_id = uuid4()

    monkeypatch.setattr(
        CollectionService,
        "list_episodes",
        lambda _session, **kwargs: [
            {
                "collection_entry_id": collection_entry_id,
                "source": "jellyfin",
                "source_item_id": "jf-episode-1",
                "media_item_id": media_item_id,
                "show_id": show_id,
                "show_title": "The X-Files",
                "title": "Pilot",
                "season_number": 1,
                "episode_number": 1,
                "year": 1993,
                "tmdb_id": None,
                "imdb_id": None,
                "tvdb_id": None,
                "is_present": True,
                "first_seen_at": datetime.now(UTC),
                "last_seen_at": datetime.now(UTC),
                "missing_since": None,
                "library_id": "tv",
                "library_name": "TV Shows",
                "added_at": datetime.now(UTC),
                "runtime_seconds": 2800,
                "file_path": "D:/media/tv/X-Files/S01E01.mkv",
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/collection/episodes?query=x-files")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["show_title"] == "The X-Files"
    assert payload[0]["episode_number"] == 1
