from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.shows import ShowService


class DummyShow:
    def __init__(self) -> None:
        self.show_id = uuid4()
        self.tmdb_id = 204154
        self.tvdb_id = 421287
        self.imdb_id = "tt21056886"
        self.title = "Scavengers Reign"
        self.year = 2023
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)


def test_list_shows_returns_rows(monkeypatch) -> None:
    monkeypatch.setattr(
        ShowService,
        "list_shows",
        lambda _session: [DummyShow()],
    )

    client = TestClient(app)
    response = client.get("/api/v1/shows")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Scavengers Reign"


def test_list_show_progress_returns_rows(monkeypatch) -> None:
    user_id = uuid4()
    show_id = uuid4()

    monkeypatch.setattr(
        ShowService,
        "list_show_progress",
        lambda _session, *, user_id=None: [
            {
                "show_id": show_id,
                "show_tmdb_id": 204154,
                "show_title": "Scavengers Reign",
                "user_id": user_id,
                "total_episodes": 12,
                "watched_episodes": 6,
                "watched_percent": Decimal("50.00"),
            }
        ],
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/shows/progress?user_id={user_id}")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["show_title"] == "Scavengers Reign"
    assert payload[0]["watched_percent"] == "50.00"


def test_list_show_progress_invalid_user_id_returns_422(monkeypatch) -> None:
    client = TestClient(app)
    response = client.get("/api/v1/shows/progress?user_id=bad")

    assert response.status_code == 422


def test_get_show_detail_returns_payload(monkeypatch) -> None:
    show = DummyShow()
    user_id = uuid4()

    monkeypatch.setattr(
        ShowService,
        "get_show_detail",
        lambda _session, *, show_id, user_id=None: {
            "show": show,
            "progress": [
                {
                    "show_id": show.show_id,
                    "show_tmdb_id": show.tmdb_id,
                    "show_title": show.title,
                    "user_id": user_id,
                    "total_episodes": 12,
                    "watched_episodes": 6,
                    "watched_percent": Decimal("50.00"),
                }
            ],
            "episodes": [
                {
                    "media_item_id": uuid4(),
                    "title": "The Nest",
                    "season_number": 1,
                    "episode_number": 8,
                    "watched_count": 1,
                    "watched_by_user": True,
                }
            ],
        },
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/shows/{show.show_id}?user_id={user_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["show"]["title"] == "Scavengers Reign"
    assert payload["progress"][0]["watched_percent"] == "50.00"
    assert payload["episodes"][0]["title"] == "The Nest"


def test_get_show_detail_not_found_returns_404(monkeypatch) -> None:
    from app.services.shows import ShowNotFoundError

    monkeypatch.setattr(
        ShowService,
        "get_show_detail",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            ShowNotFoundError("Show not found")
        ),
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/shows/{uuid4()}")

    assert response.status_code == 404
