from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from app.schemas.jellyfin_integration import JellyfinWebhookPayload
from app.services.jellyfin_webhooks import JellyfinWebhookService
from app.services.playback_events import PlaybackEventDuplicateError


JELLYFIN_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
ITEM_ID = "22222222222222222222222222222222"


def _payload(**updates) -> JellyfinWebhookPayload:
    values = {
        "notification_type": "PlaybackStop",
        "server_id": "server-1",
        "occurred_at": datetime(2026, 8, 20, 12, tzinfo=UTC),
        "jellyfin_user_id": JELLYFIN_USER_ID,
        "item_id": ITEM_ID,
        "item_type": "Movie",
        "title": "Alien",
        "year": 1979,
        "runtime_ticks": 70_200_000_000,
        "playback_position_ticks": 68_800_000_000,
        "played_to_completion": True,
        "device_id": "kodi-living-room",
        "tmdb_id": 348,
    }
    values.update(updates)
    return JellyfinWebhookPayload(**values)


def _install_mapped_user(monkeypatch):
    user = SimpleNamespace(user_id=uuid4(), jellyfin_user_id=JELLYFIN_USER_ID)
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.UserService.get_user_by_jellyfin_user_id",
        lambda *_args, **_kwargs: user,
    )
    return user


def test_start_is_recorded_without_watch(monkeypatch) -> None:
    session = Mock()
    _install_mapped_user(monkeypatch)
    recorded = SimpleNamespace(playback_event_id=uuid4())
    updated = SimpleNamespace(playback_event_id=recorded.playback_event_id)
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: updated,
    )

    result = JellyfinWebhookService.ingest(
        session,
        payload=_payload(notification_type="PlaybackStart"),
    )

    assert result.action == "recorded_only"
    assert result.watch_event is None
    assert "start" in result.reason.lower()


def test_completed_stop_creates_watch_with_duration(monkeypatch) -> None:
    session = Mock()
    user = _install_mapped_user(monkeypatch)
    recorded = SimpleNamespace(playback_event_id=uuid4())
    media_item = SimpleNamespace(media_item_id=uuid4())
    watch_event = SimpleNamespace(watch_id=uuid4())
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.media_item_repository.find_media_item_by_jellyfin_item_id",
        lambda *_args, **_kwargs: media_item,
    )

    def fake_create(*_args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(created=True, watch_event=watch_event)

    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.WatchEventService.create_watch_event",
        fake_create,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: recorded,
    )

    result = JellyfinWebhookService.ingest(session, payload=_payload())

    assert result.action == "watch_event_created"
    assert captured["user_id"] == user.user_id
    assert captured["media_item_id"] == media_item.media_item_id
    assert captured["total_seconds"] == 7020
    assert captured["watched_seconds"] == 6880
    assert captured["progress_percent"] == Decimal("98.01")
    assert captured["origin_playback_event_id"] == recorded.playback_event_id


def test_unmatched_completed_stop_remains_raw_event(monkeypatch) -> None:
    session = Mock()
    _install_mapped_user(monkeypatch)
    recorded = SimpleNamespace(playback_event_id=uuid4())
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.PlaybackEventService.record_playback_event",
        lambda *_args, **_kwargs: recorded,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.media_item_repository.find_media_item_by_jellyfin_item_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.PlaybackEventService.update_playback_event_decision",
        lambda *_args, **_kwargs: recorded,
    )

    result = JellyfinWebhookService.ingest(session, payload=_payload())

    assert result.action == "recorded_only"
    assert "not mapped" in result.reason


def test_duplicate_delivery_returns_existing_decision(monkeypatch) -> None:
    session = Mock()
    _install_mapped_user(monkeypatch)
    existing = SimpleNamespace(playback_event_id=uuid4(), watch_id=None)

    def duplicate(*_args, **_kwargs):
        raise PlaybackEventDuplicateError("duplicate")

    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.PlaybackEventService.record_playback_event",
        duplicate,
    )
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.playback_event_repository.get_playback_event_by_source_event_id",
        lambda *_args, **_kwargs: existing,
    )

    result = JellyfinWebhookService.ingest(session, payload=_payload())

    assert result.action == "duplicate_event_ignored"
    assert result.playback_event is existing


def test_unmapped_user_is_rejected_before_recording(monkeypatch) -> None:
    session = Mock()
    monkeypatch.setattr(
        "app.services.jellyfin_webhooks.UserService.get_user_by_jellyfin_user_id",
        lambda *_args, **_kwargs: None,
    )

    with pytest.raises(ValueError, match="not mapped"):
        JellyfinWebhookService.ingest(session, payload=_payload())
