from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

from app.schemas.webhooks import KodiPlaybackEventPayload
from app.services.webhooks import WebhookService


def test_ingest_kodi_pause_records_without_watch_event(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()
    updated_event = Mock()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: updated_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.get_session_max_progress_percent",
        lambda *_args, **_kwargs: None,
    )

    result = WebhookService.ingest_kodi_playback_event(
        session,
        payload=KodiPlaybackEventPayload(
            user_id=uuid4(),
            event_type="pause",
            occurred_at=datetime.now(UTC),
            source_event_id="evt-1",
            session_key="session-1",
            media_type="movie",
            title="The Matrix",
            year=1999,
            tmdb_id=603,
            total_seconds=7200,
            watched_seconds=3240,
            progress_percent=Decimal("45.00"),
        ),
    )

    assert result.action == "recorded_only"
    assert result.playback_event is updated_event
    assert result.watch_event is None


def test_ingest_kodi_stop_creates_watch_event(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()
    updated_event = Mock()
    existing_movie = Mock()
    existing_movie.media_item_id = uuid4()
    created_watch_event = Mock()
    created_watch_event.watch_id = uuid4()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: updated_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.source_event_exists",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.session_has_prior_scrobble_candidate",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.get_session_max_progress_percent",
        lambda *_args, **_kwargs: 95.0,
    )
    monkeypatch.setattr(
        "app.services.webhooks.MediaItemService.find_media_item_by_external_ids",
        lambda *_args, **_kwargs: existing_movie,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.create_watch_event",
        lambda *_args, **_kwargs: created_watch_event,
    )

    result = WebhookService.ingest_kodi_playback_event(
        session,
        payload=KodiPlaybackEventPayload(
            user_id=uuid4(),
            event_type="stop",
            occurred_at=datetime.now(UTC),
            source_event_id="evt-2",
            session_key="session-2",
            media_type="movie",
            title="The Matrix",
            year=1999,
            tmdb_id=603,
            total_seconds=7200,
            watched_seconds=6840,
            progress_percent=Decimal("95.00"),
        ),
    )

    assert result.action == "watch_event_created"
    assert result.playback_event is updated_event
    assert result.watch_event is created_watch_event


def test_ingest_kodi_stop_skips_duplicate_watch_event(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()
    updated_event = Mock()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: updated_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.source_event_exists",
        lambda *_args, **_kwargs: True,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.get_session_max_progress_percent",
        lambda *_args, **_kwargs: 96.0,
    )

    result = WebhookService.ingest_kodi_playback_event(
        session,
        payload=KodiPlaybackEventPayload(
            user_id=uuid4(),
            event_type="stop",
            occurred_at=datetime.now(UTC),
            source_event_id="evt-3",
            session_key="session-3",
            media_type="movie",
            title="The Matrix",
            year=1999,
            tmdb_id=603,
            total_seconds=7200,
            watched_seconds=6912,
            progress_percent=Decimal("96.00"),
        ),
    )

    assert result.action == "duplicate_watch_event_skipped"
    assert result.playback_event is updated_event
    assert result.watch_event is None


def test_ingest_kodi_stop_skips_when_session_already_scrobbled(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()
    recorded_event.playback_event_id = uuid4()
    updated_event = Mock()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: updated_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.source_event_exists",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.session_has_prior_scrobble_candidate",
        lambda *_args, **_kwargs: True,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.get_session_max_progress_percent",
        lambda *_args, **_kwargs: 96.0,
    )

    result = WebhookService.ingest_kodi_playback_event(
        session,
        payload=KodiPlaybackEventPayload(
            user_id=uuid4(),
            event_type="stop",
            occurred_at=datetime.now(UTC),
            source_event_id="evt-4",
            session_key="session-4",
            media_type="movie",
            title="The Matrix",
            year=1999,
            tmdb_id=603,
            total_seconds=7200,
            watched_seconds=6912,
            progress_percent=Decimal("96.00"),
        ),
    )

    assert result.action == "duplicate_watch_event_skipped"
    assert result.playback_event is updated_event
    assert result.watch_event is None
    assert result.reason == "Playback session already produced a watch event"


def test_ingest_kodi_stop_uses_prior_session_progress_to_create_watch_event(
    monkeypatch,
) -> None:
    session = Mock()
    recorded_event = Mock()
    recorded_event.playback_event_id = uuid4()
    updated_event = Mock()
    existing_movie = Mock()
    existing_movie.media_item_id = uuid4()
    created_watch_event = Mock()
    created_watch_event.watch_id = uuid4()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: updated_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.source_event_exists",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.session_has_prior_scrobble_candidate",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.get_session_max_progress_percent",
        lambda *_args, **_kwargs: 93.0,
    )
    monkeypatch.setattr(
        "app.services.webhooks.MediaItemService.find_media_item_by_external_ids",
        lambda *_args, **_kwargs: existing_movie,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.create_watch_event",
        lambda *_args, **_kwargs: created_watch_event,
    )

    result = WebhookService.ingest_kodi_playback_event(
        session,
        payload=KodiPlaybackEventPayload(
            user_id=uuid4(),
            event_type="stop",
            occurred_at=datetime.now(UTC),
            source_event_id="evt-5",
            session_key="session-5",
            media_type="movie",
            title="The Matrix",
            year=1999,
            tmdb_id=603,
            total_seconds=7200,
            watched_seconds=5904,
            progress_percent=Decimal("82.00"),
        ),
    )

    assert result.action == "watch_event_created"
    assert result.playback_event is updated_event
    assert result.watch_event is created_watch_event


def test_ingest_kodi_stop_uses_duration_ratio_when_progress_missing(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()
    recorded_event.playback_event_id = uuid4()
    updated_event = Mock()
    existing_movie = Mock()
    existing_movie.media_item_id = uuid4()
    created_watch_event = Mock()
    created_watch_event.watch_id = uuid4()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: updated_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.source_event_exists",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.session_has_prior_scrobble_candidate",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "app.services.webhooks.MediaItemService.find_media_item_by_external_ids",
        lambda *_args, **_kwargs: existing_movie,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.create_watch_event",
        lambda *_args, **_kwargs: created_watch_event,
    )

    result = WebhookService.ingest_kodi_playback_event(
        session,
        payload=KodiPlaybackEventPayload(
            user_id=uuid4(),
            event_type="stop",
            occurred_at=datetime.now(UTC),
            source_event_id="evt-6",
            session_key="session-6",
            media_type="movie",
            title="The Matrix",
            year=1999,
            tmdb_id=603,
            total_seconds=7200,
            watched_seconds=6840,
            progress_percent=None,
        ),
    )

    assert result.action == "watch_event_created"
    assert result.playback_event is updated_event
    assert result.watch_event is created_watch_event


def test_ingest_kodi_stop_records_only_when_duration_ratio_is_low(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()
    updated_event = Mock()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: updated_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.get_session_max_progress_percent",
        lambda *_args, **_kwargs: None,
    )

    result = WebhookService.ingest_kodi_playback_event(
        session,
        payload=KodiPlaybackEventPayload(
            user_id=uuid4(),
            event_type="stop",
            occurred_at=datetime.now(UTC),
            source_event_id="evt-7",
            session_key="session-7",
            media_type="movie",
            title="The Matrix",
            year=1999,
            tmdb_id=603,
            total_seconds=7200,
            watched_seconds=3600,
            progress_percent=None,
        ),
    )

    assert result.action == "recorded_only"
    assert result.playback_event is updated_event
    assert result.watch_event is None
