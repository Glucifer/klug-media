from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.services.shows import ShowNotFoundError, ShowService


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


def test_get_show_detail_returns_show_progress_and_episodes(monkeypatch) -> None:
    session = object()
    show = DummyShow()
    user_id = uuid4()

    monkeypatch.setattr(
        "app.services.shows.show_repository.find_show_by_id",
        lambda _session, *, show_id: show,
    )
    monkeypatch.setattr(
        "app.services.shows.show_repository.list_show_progress",
        lambda _session, *, user_id, show_id: [{"show_id": show_id, "user_id": user_id}],
    )
    monkeypatch.setattr(
        "app.services.shows.show_repository.list_show_episodes",
        lambda _session, *, show_id, user_id: [{"media_item_id": uuid4(), "title": "Ep"}],
    )

    result = ShowService.get_show_detail(session, show_id=show.show_id, user_id=user_id)
    assert result["show"] is show
    assert len(result["progress"]) == 1
    assert len(result["episodes"]) == 1


def test_get_show_detail_not_found_raises(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.shows.show_repository.find_show_by_id",
        lambda _session, *, show_id: None,
    )

    with pytest.raises(ShowNotFoundError):
        ShowService.get_show_detail(object(), show_id=uuid4(), user_id=None)
