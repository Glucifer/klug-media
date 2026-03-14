from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.playback_events import (
    PlaybackEventConstraintError,
    PlaybackEventDuplicateError,
    PlaybackEventService,
)


def test_record_playback_event_normalizes_input(monkeypatch) -> None:
    session = Mock()
    expected_event = Mock()

    def fake_create_playback_event(_session, **kwargs):
        assert kwargs["collector"] == "node_red"
        assert kwargs["playback_source"] == "kodi"
        assert kwargs["event_type"] == "stop"
        assert kwargs["title"] == "The Matrix"
        assert kwargs["imdb_id"] == "tt0133093"
        return expected_event

    monkeypatch.setattr(
        "app.services.playback_events.playback_event_repository.create_playback_event",
        fake_create_playback_event,
    )

    event = PlaybackEventService.record_playback_event(
        session,
        collector=" node_red ",
        playback_source=" kodi ",
        event_type=" stop ",
        user_id=uuid4(),
        occurred_at=datetime.now(UTC),
        source_event_id=" evt-1 ",
        session_key=" session-1 ",
        media_type="movie",
        title=" The Matrix ",
        year=1999,
        season_number=None,
        episode_number=None,
        tmdb_id=603,
        imdb_id=" tt0133093 ",
        tvdb_id=None,
        progress_percent=Decimal("97.50"),
        payload={"state": "stopped"},
    )

    assert event is expected_event
    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_record_playback_event_empty_title_raises_value_error() -> None:
    session = Mock()

    with pytest.raises(ValueError):
        PlaybackEventService.record_playback_event(
            session,
            collector="node_red",
            playback_source="kodi",
            event_type="stop",
            user_id=uuid4(),
            occurred_at=datetime.now(UTC),
            source_event_id=None,
            session_key=None,
            media_type="movie",
            title="   ",
            year=None,
            season_number=None,
            episode_number=None,
            tmdb_id=None,
            imdb_id=None,
            tvdb_id=None,
            progress_percent=None,
            payload={},
        )


def test_record_playback_event_duplicate_maps_to_domain_error(monkeypatch) -> None:
    session = Mock()

    duplicate_exc = IntegrityError("insert", {}, Exception("duplicate"))
    duplicate_exc.orig.diag = type(
        "Diag", (), {"constraint_name": "ux_playback_event_source_event"}
    )()

    def fake_create_playback_event(_session, **_kwargs):
        raise duplicate_exc

    monkeypatch.setattr(
        "app.services.playback_events.playback_event_repository.create_playback_event",
        fake_create_playback_event,
    )

    with pytest.raises(PlaybackEventDuplicateError):
        PlaybackEventService.record_playback_event(
            session,
            collector="node_red",
            playback_source="kodi",
            event_type="stop",
            user_id=uuid4(),
            occurred_at=datetime.now(UTC),
            source_event_id="evt-1",
            session_key=None,
            media_type="movie",
            title="The Matrix",
            year=1999,
            season_number=None,
            episode_number=None,
            tmdb_id=603,
            imdb_id=None,
            tvdb_id=None,
            progress_percent=Decimal("98.00"),
            payload={},
        )

    session.rollback.assert_called_once()


def test_record_playback_event_integrity_error_maps_to_constraint_error(
    monkeypatch,
) -> None:
    session = Mock()

    def fake_create_playback_event(_session, **_kwargs):
        raise IntegrityError("insert", {}, Exception("fk violation"))

    monkeypatch.setattr(
        "app.services.playback_events.playback_event_repository.create_playback_event",
        fake_create_playback_event,
    )

    with pytest.raises(PlaybackEventConstraintError):
        PlaybackEventService.record_playback_event(
            session,
            collector="node_red",
            playback_source="kodi",
            event_type="stop",
            user_id=uuid4(),
            occurred_at=datetime.now(UTC),
            source_event_id="evt-1",
            session_key=None,
            media_type="movie",
            title="The Matrix",
            year=1999,
            season_number=None,
            episode_number=None,
            tmdb_id=603,
            imdb_id=None,
            tvdb_id=None,
            progress_percent=Decimal("98.00"),
            payload={},
        )

    session.rollback.assert_called_once()
