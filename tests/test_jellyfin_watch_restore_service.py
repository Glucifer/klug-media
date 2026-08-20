from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID, uuid4

from app.schemas.jellyfin_integration import JellyfinWatchRestoreRequest
from app.services.jellyfin import (
    JellyfinPlayedItem,
    JellyfinPlayedUpdateResult,
)
from app.services.jellyfin_watch_restore import JellyfinWatchRestoreService


JELLYFIN_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
PLAYED_ITEM_ID = "22222222222222222222222222222222"
MOVIE_ITEM_ID = "33333333333333333333333333333333"
EPISODE_ITEM_ID = "44444444444444444444444444444444"


class DummyClient:
    def __init__(self, *, failed_item_id: str | None = None) -> None:
        self.failed_item_id = failed_item_id
        self.marked = []

    def list_played_items(self, *, user_id, changed_since=None):
        assert user_id == JELLYFIN_USER_ID
        assert changed_since is None
        return [
            JellyfinPlayedItem(
                source_item_id=PLAYED_ITEM_ID,
                item_type="movie",
                title="Already Played",
                year=2000,
                season_number=None,
                episode_number=None,
                show_title=None,
                tmdb_id=None,
                imdb_id=None,
                tvdb_id=None,
                runtime_seconds=3600,
                played=True,
                play_count=1,
                last_played_at=datetime(2026, 1, 1, tzinfo=UTC),
                source_data={},
            )
        ]

    def mark_items_played(self, *, user_id, updates):
        assert user_id == JELLYFIN_USER_ID
        self.marked.extend(updates)
        return [
            JellyfinPlayedUpdateResult(
                item_id=update.item_id,
                succeeded=update.item_id != self.failed_item_id,
                error=(
                    "Jellyfin request failed with status 500"
                    if update.item_id == self.failed_item_id
                    else None
                ),
            )
            for update in updates
        ]


def _install_candidates(monkeypatch):
    user = SimpleNamespace(user_id=uuid4(), jellyfin_user_id=JELLYFIN_USER_ID)
    candidates = [
        {
            "item_id": PLAYED_ITEM_ID,
            "title": "Already Played",
            "media_type": "movie",
            "last_watched_at": datetime(2025, 1, 1, tzinfo=UTC),
        },
        {
            "item_id": MOVIE_ITEM_ID,
            "title": "Alien",
            "media_type": "movie",
            "last_watched_at": datetime(2025, 2, 1, tzinfo=UTC),
        },
        {
            "item_id": EPISODE_ITEM_ID,
            "title": "Pilot",
            "media_type": "episode",
            "last_watched_at": datetime(2025, 3, 1, tzinfo=UTC),
        },
    ]
    monkeypatch.setattr(
        "app.services.jellyfin_watch_restore.UserService.get_user_by_id",
        lambda *_args, **_kwargs: user,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_watch_restore.media_item_repository.list_present_jellyfin_watched_items",
        lambda *_args, **_kwargs: candidates,
    )
    return user


def test_dry_run_reports_all_candidates_without_writes(monkeypatch) -> None:
    session = Mock()
    user = _install_candidates(monkeypatch)
    client = DummyClient()

    result = JellyfinWatchRestoreService.run(
        session,
        payload=JellyfinWatchRestoreRequest(
            klug_user_id=user.user_id,
            dry_run=True,
            batch_size=1,
        ),
        client=client,
    )

    assert result.status == "dry_run"
    assert result.eligible_count == 3
    assert result.already_played_count == 1
    assert result.candidate_count == 2
    assert result.movie_candidate_count == 1
    assert result.episode_candidate_count == 1
    assert result.remaining_count == 2
    assert client.marked == []


def test_real_restore_is_bounded_and_uses_latest_watch_date(monkeypatch) -> None:
    session = Mock()
    user = _install_candidates(monkeypatch)
    client = DummyClient()
    batch_id = uuid4()
    finish = Mock(return_value=SimpleNamespace(import_batch_id=batch_id))
    monkeypatch.setattr(
        "app.services.jellyfin_watch_restore.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id),
    )
    monkeypatch.setattr(
        "app.services.jellyfin_watch_restore.ImportBatchService.finish_import_batch",
        finish,
    )

    result = JellyfinWatchRestoreService.run(
        session,
        payload=JellyfinWatchRestoreRequest(
            klug_user_id=user.user_id,
            dry_run=False,
            batch_size=1,
        ),
        client=client,
    )

    assert result.status == "partial"
    assert result.attempted_count == 1
    assert result.restored_count == 1
    assert result.remaining_count == 1
    assert client.marked[0].item_id == MOVIE_ITEM_ID
    assert client.marked[0].date_played == datetime(2025, 2, 1, tzinfo=UTC)
    assert finish.call_args.kwargs["status"] == "completed"


def test_failed_updates_are_reported_and_audited(monkeypatch) -> None:
    session = Mock()
    user = _install_candidates(monkeypatch)
    client = DummyClient(failed_item_id=MOVIE_ITEM_ID)
    batch_id = uuid4()
    add_error = Mock()
    monkeypatch.setattr(
        "app.services.jellyfin_watch_restore.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id),
    )
    monkeypatch.setattr(
        "app.services.jellyfin_watch_restore.ImportBatchService.add_import_batch_error",
        add_error,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_watch_restore.ImportBatchService.finish_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id),
    )

    result = JellyfinWatchRestoreService.run(
        session,
        payload=JellyfinWatchRestoreRequest(
            klug_user_id=user.user_id,
            dry_run=False,
            batch_size=1,
        ),
        client=client,
    )

    assert result.status == "partial_with_errors"
    assert result.restored_count == 0
    assert result.error_count == 1
    assert result.issues[0].item_id == MOVIE_ITEM_ID
    add_error.assert_called_once()
