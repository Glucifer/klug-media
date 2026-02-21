from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.services.show_backfill import ShowBackfillService


def test_backfill_dry_run_reports_without_writes(monkeypatch) -> None:
    episodes = [
        SimpleNamespace(show_tmdb_id=100, show_id=None),
        SimpleNamespace(show_tmdb_id=100, show_id=None),
        SimpleNamespace(show_tmdb_id=200, show_id=None),
    ]
    session = Mock()

    monkeypatch.setattr(
        "app.services.show_backfill.media_item_repository.list_episode_media_items_missing_show_id",
        lambda *_args, **_kwargs: episodes,
    )
    monkeypatch.setattr(
        "app.services.show_backfill.ShowService.find_show_by_tmdb_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.show_backfill.ShowService.get_or_create_show",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("dry-run should not create shows")
        ),
    )

    result = ShowBackfillService.backfill_episode_show_links(
        session,
        dry_run=True,
    )

    assert result.scanned_count == 3
    assert result.linked_count == 3
    assert result.shows_created_count == 2
    assert result.dry_run is True
    session.commit.assert_not_called()
    assert episodes[0].show_id is None


def test_backfill_non_dry_links_rows_and_creates_missing_shows(monkeypatch) -> None:
    existing_show = SimpleNamespace(show_id=uuid4())
    created_show = SimpleNamespace(show_id=uuid4())
    episodes = [
        SimpleNamespace(show_tmdb_id=100, show_id=None),
        SimpleNamespace(show_tmdb_id=200, show_id=None),
    ]
    session = Mock()

    monkeypatch.setattr(
        "app.services.show_backfill.media_item_repository.list_episode_media_items_missing_show_id",
        lambda *_args, **_kwargs: episodes,
    )

    def fake_find_show(_session, *, tmdb_id: int):
        if tmdb_id == 100:
            return existing_show
        return None

    monkeypatch.setattr(
        "app.services.show_backfill.ShowService.find_show_by_tmdb_id",
        fake_find_show,
    )
    monkeypatch.setattr(
        "app.services.show_backfill.media_item_repository.find_show_media_item_by_tmdb_id",
        lambda *_args, **_kwargs: SimpleNamespace(
            title="Show Name",
            year=2024,
            tvdb_id=123,
            imdb_id="tt123",
        ),
    )
    monkeypatch.setattr(
        "app.services.show_backfill.ShowService.get_or_create_show",
        lambda *_args, **_kwargs: created_show,
    )

    result = ShowBackfillService.backfill_episode_show_links(
        session,
        dry_run=False,
    )

    assert result.scanned_count == 2
    assert result.linked_count == 2
    assert result.shows_created_count == 1
    assert result.dry_run is False
    assert episodes[0].show_id == existing_show.show_id
    assert episodes[1].show_id == created_show.show_id
    session.commit.assert_called_once()
