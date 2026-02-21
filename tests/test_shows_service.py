from datetime import UTC, datetime
from uuid import uuid4

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


def test_list_shows_returns_repository_data(monkeypatch) -> None:
    expected = [DummyShow()]
    session = object()

    monkeypatch.setattr(
        "app.services.shows.show_repository.list_shows",
        lambda _session: expected,
    )

    result = ShowService.list_shows(session)
    assert result == expected


def test_list_show_progress_parses_user_id(monkeypatch) -> None:
    session = object()
    user_id = uuid4()
    captured: dict[str, object] = {}

    def fake_list_show_progress(_session, *, user_id):
        captured["user_id"] = user_id
        return []

    monkeypatch.setattr(
        "app.services.shows.show_repository.list_show_progress",
        fake_list_show_progress,
    )

    ShowService.list_show_progress(session, user_id=user_id)
    assert captured["user_id"] == user_id
