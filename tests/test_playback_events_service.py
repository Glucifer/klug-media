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
        assert kwargs["total_seconds"] == 7200
        assert kwargs["watched_seconds"] == 7020
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
        total_seconds=7200,
        watched_seconds=7020,
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
            total_seconds=None,
            watched_seconds=None,
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
            total_seconds=None,
            watched_seconds=None,
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
            total_seconds=None,
            watched_seconds=None,
            progress_percent=Decimal("98.00"),
            payload={},
        )

    session.rollback.assert_called_once()


def test_session_has_prior_scrobble_candidate_normalizes_input(monkeypatch) -> None:
    session = Mock()

    def fake_session_has_prior_scrobble_candidate(_session, **kwargs):
        assert kwargs["collector"] == "node_red"
        assert kwargs["playback_source"] == "kodi"
        assert kwargs["session_key"] == "session-1"
        return True

    monkeypatch.setattr(
        "app.services.playback_events.playback_event_repository.session_has_prior_scrobble_candidate",
        fake_session_has_prior_scrobble_candidate,
    )

    result = PlaybackEventService.session_has_prior_scrobble_candidate(
        session,
        collector=" node_red ",
        playback_source=" kodi ",
        user_id=uuid4(),
        session_key=" session-1 ",
        exclude_playback_event_id=uuid4(),
    )

    assert result is True


def test_get_session_max_progress_percent_normalizes_input(monkeypatch) -> None:
    session = Mock()

    def fake_get_session_max_progress_percent(_session, **kwargs):
        assert kwargs["collector"] == "node_red"
        assert kwargs["playback_source"] == "kodi"
        assert kwargs["session_key"] == "session-1"
        return 96.5

    monkeypatch.setattr(
        "app.services.playback_events.playback_event_repository.get_session_max_progress_percent",
        fake_get_session_max_progress_percent,
    )

    result = PlaybackEventService.get_session_max_progress_percent(
        session,
        collector=" node_red ",
        playback_source=" kodi ",
        user_id=uuid4(),
        session_key=" session-1 ",
    )

    assert result == 96.5


def test_update_playback_event_decision_normalizes_input(monkeypatch) -> None:
    session = Mock()
    playback_event = Mock()
    updated_event = Mock()

    def fake_update_playback_event_decision(_session, **kwargs):
        assert kwargs["decision_status"] == "watch_event_created"
        assert kwargs["decision_reason"] == "Created from stop event"
        return updated_event

    monkeypatch.setattr(
        "app.services.playback_events.playback_event_repository.update_playback_event_decision",
        fake_update_playback_event_decision,
    )

    event = PlaybackEventService.update_playback_event_decision(
        session,
        playback_event=playback_event,
        decision_status=" watch_event_created ",
        decision_reason=" Created from stop event ",
        watch_id=uuid4(),
    )

    assert event is updated_event
    session.commit.assert_called_once()
    session.rollback.assert_not_called()
