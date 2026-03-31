from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.watch_events import WatchEventConstraintError, WatchEventService


def test_create_watch_event_normalizes_input(monkeypatch) -> None:
    session = Mock()
    expected_event = Mock()

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.get_watch_event_by_source_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.find_matching_watch_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.prior_watch_event_exists",
        lambda *_args, **_kwargs: False,
    )

    def fake_create_watch_event(_session, **kwargs):
        assert kwargs["playback_source"] == "jellyfin"
        assert kwargs["rating_scale"] == "5-star"
        assert kwargs["origin_kind"] == "manual_entry"
        assert kwargs["origin_playback_event_id"] is None
        assert kwargs["rewatch"] is False
        return expected_event

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.create_watch_event",
        fake_create_watch_event,
    )

    result = WatchEventService.create_watch_event(
        session,
        user_id=uuid4(),
        media_item_id=uuid4(),
        watched_at=datetime.now(UTC),
        playback_source=" jellyfin ",
        total_seconds=7000,
        watched_seconds=6900,
        progress_percent=Decimal("98.00"),
        completed=True,
        rating_value=Decimal("4.00"),
        rating_scale=" 5-star ",
        media_version_id=None,
        source_event_id="evt-1",
    )

    assert result.watch_event is expected_event
    assert result.created is True
    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_create_watch_event_empty_playback_source_raises_value_error() -> None:
    session = Mock()

    with pytest.raises(ValueError):
        WatchEventService.create_watch_event(
            session,
            user_id=uuid4(),
            media_item_id=uuid4(),
            watched_at=datetime.now(UTC),
            playback_source="   ",
            total_seconds=None,
            watched_seconds=None,
            progress_percent=None,
            completed=True,
            rating_value=None,
            rating_scale=None,
            media_version_id=None,
            source_event_id=None,
        )


def test_create_watch_event_naive_watched_at_raises_value_error() -> None:
    session = Mock()

    with pytest.raises(
        ValueError, match="watched_at must include timezone information"
    ):
        WatchEventService.create_watch_event(
            session,
            user_id=uuid4(),
            media_item_id=uuid4(),
            watched_at=datetime(2026, 1, 1, 12, 0, 0),
            playback_source="jellyfin",
            total_seconds=None,
            watched_seconds=None,
            progress_percent=None,
            completed=True,
            rating_value=None,
            rating_scale=None,
            media_version_id=None,
            source_event_id=None,
        )


def test_create_watch_event_integrity_error_maps_to_domain_error(monkeypatch) -> None:
    session = Mock()

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.get_watch_event_by_source_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.find_matching_watch_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.prior_watch_event_exists",
        lambda *_args, **_kwargs: False,
    )

    def fake_create_watch_event(_session, **_kwargs):
        raise IntegrityError("insert", {}, Exception("fk violation"))

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.create_watch_event",
        fake_create_watch_event,
    )

    with pytest.raises(WatchEventConstraintError):
        WatchEventService.create_watch_event(
            session,
            user_id=uuid4(),
            media_item_id=uuid4(),
            watched_at=datetime.now(UTC),
            playback_source="jellyfin",
            total_seconds=None,
            watched_seconds=None,
            progress_percent=None,
            completed=True,
            rating_value=None,
            rating_scale=None,
            media_version_id=None,
            source_event_id=None,
        )

    session.rollback.assert_called_once()


def test_create_watch_event_marks_rewatch_when_prior_watch_exists(monkeypatch) -> None:
    session = Mock()
    expected_event = Mock()

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.get_watch_event_by_source_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.find_matching_watch_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.prior_watch_event_exists",
        lambda *_args, **_kwargs: True,
    )

    def fake_create_watch_event(_session, **kwargs):
        assert kwargs["rewatch"] is True
        return expected_event

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.create_watch_event",
        fake_create_watch_event,
    )

    result = WatchEventService.create_watch_event(
        session,
        user_id=uuid4(),
        media_item_id=uuid4(),
        watched_at=datetime.now(UTC),
        playback_source="jellyfin",
        total_seconds=None,
        watched_seconds=None,
        progress_percent=None,
        completed=True,
        rating_value=None,
        rating_scale=None,
        media_version_id=None,
        source_event_id="evt-2",
    )

    assert result.watch_event is expected_event
    assert result.created is True
    session.commit.assert_called_once()


def test_create_watch_event_returns_existing_source_event_match(monkeypatch) -> None:
    session = Mock()
    existing_event = Mock()

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.get_watch_event_by_source_event",
        lambda *_args, **_kwargs: existing_event,
    )

    result = WatchEventService.create_watch_event(
        session,
        user_id=uuid4(),
        media_item_id=uuid4(),
        watched_at=datetime.now(UTC),
        playback_source="jellyfin",
        total_seconds=None,
        watched_seconds=None,
        progress_percent=None,
        completed=True,
        rating_value=None,
        rating_scale=None,
        media_version_id=None,
        source_event_id="evt-existing",
    )

    assert result.watch_event is existing_event
    assert result.created is False
    assert result.match_reason == "source_event"
    session.commit.assert_not_called()


def test_create_watch_event_returns_existing_collision_match(monkeypatch) -> None:
    session = Mock()
    existing_event = Mock()

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.get_watch_event_by_source_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.find_matching_watch_event",
        lambda *_args, **_kwargs: existing_event,
    )

    result = WatchEventService.create_watch_event(
        session,
        user_id=uuid4(),
        media_item_id=uuid4(),
        watched_at=datetime.now(UTC),
        playback_source="jellyfin",
        total_seconds=None,
        watched_seconds=None,
        progress_percent=None,
        completed=True,
        rating_value=None,
        rating_scale=None,
        media_version_id=None,
        source_event_id=None,
        origin_kind="manual_import",
    )

    assert result.watch_event is existing_event
    assert result.created is False
    assert result.match_reason == "collision_window"
    session.commit.assert_not_called()


def test_list_watch_events_clamps_limit(monkeypatch) -> None:
    session = Mock()

    def fake_list_watch_events(_session, **kwargs):
        assert kwargs["limit"] == 100
        assert kwargs["offset"] == 0
        return []

    monkeypatch.setattr(
        "app.services.watch_events.watch_event_repository.list_watch_events",
        fake_list_watch_events,
    )

    WatchEventService.list_watch_events(
        session,
        user_id=None,
        media_item_id=None,
        watched_after=None,
        watched_before=None,
        local_date_from=None,
        local_date_to=None,
        media_type=None,
        limit=1000,
        offset=-5,
    )
