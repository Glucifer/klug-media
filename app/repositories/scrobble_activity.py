from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session

from app.db.models.entities import MediaItem, PlaybackEvent, User, WatchEvent


def list_scrobble_activity(
    session: Session,
    *,
    user_id: UUID | None,
    collector: str | None,
    playback_source: str | None,
    decision_status: str | None,
    event_type: str | None,
    media_type: str | None,
    occurred_after: datetime | None,
    occurred_before: datetime | None,
    only_unmatched: bool,
    only_with_watch: bool,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    statement: Select[tuple[PlaybackEvent, str | None, UUID | None, str | None, str | None]] = (
        select(
            PlaybackEvent,
            User.username,
            WatchEvent.media_item_id,
            WatchEvent.origin_kind,
            MediaItem.title,
            MediaItem.type,
        )
        .join(User, PlaybackEvent.user_id == User.user_id)
        .outerjoin(WatchEvent, PlaybackEvent.watch_id == WatchEvent.watch_id)
        .outerjoin(
            MediaItem,
            and_(
                WatchEvent.media_item_id == MediaItem.media_item_id,
                WatchEvent.media_item_id.is_not(None),
            ),
        )
    )

    if user_id is not None:
        statement = statement.where(PlaybackEvent.user_id == user_id)
    if collector is not None:
        statement = statement.where(PlaybackEvent.collector == collector)
    if playback_source is not None:
        statement = statement.where(PlaybackEvent.playback_source == playback_source)
    if decision_status is not None:
        statement = statement.where(PlaybackEvent.decision_status == decision_status)
    if event_type is not None:
        statement = statement.where(PlaybackEvent.event_type == event_type)
    if media_type is not None:
        statement = statement.where(PlaybackEvent.media_type == media_type)
    if occurred_after is not None:
        statement = statement.where(PlaybackEvent.occurred_at >= occurred_after)
    if occurred_before is not None:
        statement = statement.where(PlaybackEvent.occurred_at <= occurred_before)
    if only_unmatched:
        statement = statement.where(PlaybackEvent.watch_id.is_(None))
    if only_with_watch:
        statement = statement.where(PlaybackEvent.watch_id.is_not(None))

    statement = (
        statement.order_by(PlaybackEvent.occurred_at.desc(), PlaybackEvent.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = session.execute(statement).all()

    payload: list[dict[str, Any]] = []
    for playback_event, username, media_item_id, origin_kind, matched_title, matched_media_type in rows:
        payload.append(
            {
                "playback_event_id": playback_event.playback_event_id,
                "occurred_at": playback_event.occurred_at,
                "user_id": playback_event.user_id,
                "username": username,
                "collector": playback_event.collector,
                "playback_source": playback_event.playback_source,
                "event_type": playback_event.event_type,
                "media_type": playback_event.media_type,
                "guessed_title": playback_event.title,
                "year": playback_event.year,
                "season_number": playback_event.season_number,
                "episode_number": playback_event.episode_number,
                "tmdb_id": playback_event.tmdb_id,
                "imdb_id": playback_event.imdb_id,
                "tvdb_id": playback_event.tvdb_id,
                "progress_percent": playback_event.progress_percent,
                "decision_status": playback_event.decision_status,
                "decision_reason": playback_event.decision_reason,
                "watch_id": playback_event.watch_id,
                "media_item_id": media_item_id,
                "origin_kind": origin_kind,
                "matched_title": matched_title,
                "matched_media_type": matched_media_type,
                "result_label": _result_label(playback_event.decision_status),
                "is_unmatched": playback_event.watch_id is None or media_item_id is None,
            }
        )
    return payload


def _result_label(decision_status: str | None) -> str:
    mapping = {
        "watch_event_created": "created",
        "duplicate_watch_event_skipped": "duplicate",
        "recorded_only": "ignored",
    }
    return mapping.get(decision_status or "", decision_status or "unknown")
