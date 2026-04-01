from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.services.horrorfest import HorrorfestService


def test_sync_watch_event_creates_auto_entry_for_qualifying_movie(monkeypatch) -> None:
    session = Mock()
    watch_event = Mock()
    watch_event.watch_id = uuid4()
    watch_event.media_item_id = uuid4()
    watch_event.origin_kind = "live_playback"
    watch_event.watched_at = datetime.now(UTC)
    watch_event.is_deleted = False
    watch_event.completed = True
    watch_event.updated_by = None
    watch_event.update_reason = None
    session.get.return_value = Mock(type="movie")

    year_config = Mock()
    year_config.horrorfest_year = 2026

    created = {}

    def fake_create_entry(_session, **kwargs):
        created.update(kwargs)
        entry = Mock()
        entry.horrorfest_entry_id = uuid4()
        entry.watch_id = kwargs["watch_id"]
        entry.horrorfest_year = kwargs["horrorfest_year"]
        entry.watch_order = None
        entry.created_at = datetime.now(UTC)
        return entry

    monkeypatch.setattr(
        "app.services.horrorfest.horrorfest_repository.find_horrorfest_year_for_timestamp",
        lambda *_args, **_kwargs: year_config,
    )
    monkeypatch.setattr(
        "app.services.horrorfest.horrorfest_repository.get_active_horrorfest_entry_for_watch",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.horrorfest.horrorfest_repository.get_horrorfest_entry_for_watch_and_year",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.horrorfest.horrorfest_repository.create_horrorfest_entry",
        fake_create_entry,
    )
    monkeypatch.setattr(
        "app.services.horrorfest.horrorfest_repository.list_active_horrorfest_entries_for_year",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        "app.services.horrorfest.HorrorfestService._apply_ordered_entries",
        lambda *_args, **_kwargs: None,
    )

    HorrorfestService.sync_watch_event(session, watch_event=watch_event)

    assert created["watch_id"] == watch_event.watch_id
    assert created["horrorfest_year"] == 2026
    assert created["source_kind"] == "auto_live"


def test_sync_watch_event_removes_existing_entry_when_watch_no_longer_qualifies(monkeypatch) -> None:
    session = Mock()
    watch_event = Mock()
    watch_event.watch_id = uuid4()
    watch_event.media_item_id = uuid4()
    watch_event.watched_at = datetime.now(UTC)
    watch_event.is_deleted = True
    watch_event.completed = True
    watch_event.updated_by = "tester"
    watch_event.update_reason = "deleted"
    session.get.return_value = Mock(type="movie")

    active_entry = Mock()
    active_entry.horrorfest_year = 2026

    removed = {"called": False}
    normalized = {"year": None}

    monkeypatch.setattr(
        "app.services.horrorfest.horrorfest_repository.get_active_horrorfest_entry_for_watch",
        lambda *_args, **_kwargs: active_entry,
    )
    monkeypatch.setattr(
        "app.services.horrorfest.HorrorfestService._soft_remove_entry",
        lambda *_args, **_kwargs: removed.__setitem__("called", True),
    )
    monkeypatch.setattr(
        "app.services.horrorfest.HorrorfestService._normalize_year_orders",
        lambda *_args, **kwargs: normalized.__setitem__("year", kwargs["horrorfest_year"]),
    )

    HorrorfestService.sync_watch_event(session, watch_event=watch_event)

    assert removed["called"] is True
    assert normalized["year"] == 2026


def test_include_watch_event_rejects_out_of_window_watch(monkeypatch) -> None:
    session = Mock()
    watch_id = uuid4()
    watch_event = Mock()
    watch_event.watch_id = watch_id
    watch_event.media_item_id = uuid4()
    watch_event.watched_at = datetime(2026, 1, 1, tzinfo=UTC)
    watch_event.is_deleted = False
    watch_event.completed = True
    session.get.return_value = Mock(type="movie")

    year_config = Mock()
    year_config.horrorfest_year = 2026
    year_config.window_start_at = datetime(2026, 10, 1, tzinfo=UTC)
    year_config.window_end_at = datetime(2026, 10, 31, 23, 59, tzinfo=UTC)

    monkeypatch.setattr(
        "app.services.horrorfest.watch_event_repository.get_watch_event",
        lambda *_args, **_kwargs: watch_event,
    )
    monkeypatch.setattr(
        "app.services.horrorfest.horrorfest_repository.get_horrorfest_year",
        lambda *_args, **_kwargs: year_config,
    )

    with pytest.raises(ValueError, match="must fall inside the configured Horrorfest year window"):
        HorrorfestService.include_watch_event(
            session,
            watch_id=watch_id,
            horrorfest_year=2026,
            updated_by="tester",
            update_reason=None,
            target_order=None,
            commit=False,
        )
