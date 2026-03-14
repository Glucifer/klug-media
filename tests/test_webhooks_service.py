from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

from app.schemas.webhooks import KodiPlaybackEventPayload
from app.services.webhooks import WebhookService


def test_ingest_kodi_pause_records_without_watch_event(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
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
            progress_percent=Decimal("45.00"),
        ),
    )

    assert result.action == "recorded_only"
    assert result.playback_event is recorded_event
    assert result.watch_event is None


def test_ingest_kodi_stop_creates_watch_event(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()
    existing_movie = Mock()
    existing_movie.media_item_id = uuid4()
    created_watch_event = Mock()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.source_event_exists",
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
            source_event_id="evt-2",
            session_key="session-2",
            media_type="movie",
            title="The Matrix",
            year=1999,
            tmdb_id=603,
            progress_percent=Decimal("95.00"),
        ),
    )

    assert result.action == "watch_event_created"
    assert result.playback_event is recorded_event
    assert result.watch_event is created_watch_event


def test_ingest_kodi_stop_skips_duplicate_watch_event(monkeypatch) -> None:
    session = Mock()
    recorded_event = Mock()

    monkeypatch.setattr(
        "app.services.webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded_event,
    )
    monkeypatch.setattr(
        "app.services.webhooks.WatchEventService.source_event_exists",
        lambda *_args, **_kwargs: True,
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
            progress_percent=Decimal("96.00"),
        ),
    )

    assert result.action == "duplicate_watch_event_skipped"
    assert result.playback_event is recorded_event
    assert result.watch_event is None
