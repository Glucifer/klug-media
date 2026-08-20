from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID, uuid4

from app.schemas.jellyfin_integration import JellyfinReconcileRequest
from app.services.jellyfin import JellyfinPlayedItem
from app.services.jellyfin_reconciliation import JellyfinReconciliationService


JELLYFIN_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
ITEM_ID = "22222222222222222222222222222222"


class DummyClient:
    def __init__(self, items) -> None:
        self.items = items
        self.calls: list[tuple[UUID, datetime | None]] = []

    def list_played_items(self, *, user_id, changed_since=None):
        self.calls.append((user_id, changed_since))
        return self.items


def _played_item(**updates) -> JellyfinPlayedItem:
    values = {
        "source_item_id": ITEM_ID,
        "item_type": "movie",
        "title": "Alien",
        "year": 1979,
        "season_number": None,
        "episode_number": None,
        "show_title": None,
        "tmdb_id": 348,
        "imdb_id": "tt0078748",
        "tvdb_id": None,
        "runtime_seconds": 7020,
        "played": True,
        "play_count": 1,
        "last_played_at": datetime(2026, 8, 19, 12, tzinfo=UTC),
        "source_data": {},
    }
    values.update(updates)
    return JellyfinPlayedItem(**values)


def _install_user_and_cursor(monkeypatch, *, latest_batch=None):
    user = SimpleNamespace(
        user_id=uuid4(),
        jellyfin_user_id=JELLYFIN_USER_ID,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.UserService.get_user_by_id",
        lambda *_args, **_kwargs: user,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.ImportBatchService.get_latest_completed_import_batch_for_source",
        lambda *_args, **_kwargs: latest_batch,
    )
    return user


def test_first_dry_run_uses_90_day_lookback_without_writes(monkeypatch) -> None:
    session = Mock()
    now = datetime(2026, 8, 20, 12, tzinfo=UTC)
    user = _install_user_and_cursor(monkeypatch)
    media_item = SimpleNamespace(media_item_id=uuid4())
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.media_item_repository.find_media_item_by_jellyfin_item_id",
        lambda *_args, **_kwargs: media_item,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.watch_event_repository.find_matching_watch_event",
        lambda *_args, **_kwargs: None,
    )
    client = DummyClient([_played_item()])

    result = JellyfinReconciliationService.run(
        session,
        payload=JellyfinReconcileRequest(klug_user_id=user.user_id, dry_run=True),
        client=client,
        now=now,
    )

    assert result.status == "dry_run"
    assert result.since == now - timedelta(days=90)
    assert result.inserted_count == 1
    assert result.import_batch_id.int == 0
    assert client.calls == [(JELLYFIN_USER_ID, result.since)]


def test_reconcile_reports_unmatched_missing_and_ambiguous(monkeypatch) -> None:
    session = Mock()
    now = datetime(2026, 8, 20, 12, tzinfo=UTC)
    user = _install_user_and_cursor(monkeypatch)
    media_item = SimpleNamespace(media_item_id=uuid4())

    def find_media(*_args, jellyfin_item_id, **_kwargs):
        return media_item if jellyfin_item_id == ITEM_ID else None

    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.media_item_repository.find_media_item_by_jellyfin_item_id",
        find_media,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.watch_event_repository.find_matching_watch_event",
        lambda *_args, **_kwargs: None,
    )
    client = DummyClient(
        [
            _played_item(play_count=3),
            _played_item(
                source_item_id="33333333333333333333333333333333",
                title="Unmapped",
            ),
            _played_item(
                source_item_id="44444444444444444444444444444444",
                title="No timestamp",
                last_played_at=None,
            ),
        ]
    )

    result = JellyfinReconciliationService.run(
        session,
        payload=JellyfinReconcileRequest(klug_user_id=user.user_id, dry_run=True),
        client=client,
        now=now,
    )

    assert result.scanned_count == 3
    assert result.inserted_count == 1
    assert result.unmatched_media_count == 1
    assert result.missing_timestamp_count == 1
    assert result.ambiguous_play_count == 1
    assert {issue.reason for issue in result.issues} == {
        "unmatched_media",
        "missing_last_played_at",
        "older_rewatch_dates_unavailable",
    }


def test_completed_cursor_uses_five_minute_overlap(monkeypatch) -> None:
    session = Mock()
    now = datetime(2026, 8, 20, 12, tzinfo=UTC)
    cursor = "2026-08-20T10:00:00Z"
    user = _install_user_and_cursor(
        monkeypatch,
        latest_batch=SimpleNamespace(parameters={"cursor_after": cursor}),
    )
    client = DummyClient([])

    result = JellyfinReconciliationService.run(
        session,
        payload=JellyfinReconcileRequest(klug_user_id=user.user_id, dry_run=True),
        client=client,
        now=now,
    )

    assert result.since == datetime(2026, 8, 20, 9, 55, tzinfo=UTC)


def test_real_reconcile_creates_batch_and_watch(monkeypatch) -> None:
    session = Mock()
    now = datetime(2026, 8, 20, 12, tzinfo=UTC)
    user = _install_user_and_cursor(monkeypatch)
    batch_id = uuid4()
    media_item = SimpleNamespace(media_item_id=uuid4())
    watch_event = SimpleNamespace(watch_id=uuid4())
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id),
    )
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.ImportBatchService.finish_import_batch",
        lambda *_args, **kwargs: SimpleNamespace(
            import_batch_id=kwargs["import_batch_id"]
        ),
    )
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.media_item_repository.find_media_item_by_jellyfin_item_id",
        lambda *_args, **_kwargs: media_item,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.watch_event_repository.find_matching_watch_event",
        lambda *_args, **_kwargs: None,
    )

    def fake_create(*_args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(created=True, watch_event=watch_event)

    monkeypatch.setattr(
        "app.services.jellyfin_reconciliation.WatchEventService.create_watch_event",
        fake_create,
    )

    result = JellyfinReconciliationService.run(
        session,
        payload=JellyfinReconcileRequest(klug_user_id=user.user_id, dry_run=False),
        client=DummyClient([_played_item()]),
        now=now,
    )

    assert result.status == "completed"
    assert result.import_batch_id == batch_id
    assert result.inserted_count == 1
    assert captured["origin_kind"] == "manual_import"
    assert captured["import_batch_id"] == batch_id
