from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.models.entities import MediaItem, WatchEvent


def list_watch_events(
    session: Session,
    *,
    user_id: UUID | None,
    media_item_id: UUID | None,
    watched_after: datetime | None,
    watched_before: datetime | None,
    media_type: Literal["movie", "show", "episode"] | None,
    limit: int,
    offset: int,
) -> list[WatchEvent]:
    statement: Select[tuple[WatchEvent]] = select(WatchEvent)
    if media_type is not None:
        statement = statement.join(
            MediaItem,
            WatchEvent.media_item_id == MediaItem.media_item_id,
        ).where(MediaItem.type == media_type)

    if user_id is not None:
        statement = statement.where(WatchEvent.user_id == user_id)
    if media_item_id is not None:
        statement = statement.where(WatchEvent.media_item_id == media_item_id)
    if watched_after is not None:
        statement = statement.where(WatchEvent.watched_at >= watched_after)
    if watched_before is not None:
        statement = statement.where(WatchEvent.watched_at <= watched_before)

    statement = (
        statement.order_by(WatchEvent.watched_at.desc()).offset(offset).limit(limit)
    )
    return list(session.scalars(statement))


def create_watch_event(
    session: Session,
    *,
    user_id: UUID,
    media_item_id: UUID,
    watched_at: datetime,
    playback_source: str,
    total_seconds: int | None,
    watched_seconds: int | None,
    progress_percent,
    completed: bool,
    rating_value,
    rating_scale: str | None,
    media_version_id: UUID | None,
    source_event_id: str | None,
) -> WatchEvent:
    watch_event = WatchEvent(
        user_id=user_id,
        media_item_id=media_item_id,
        watched_at=watched_at,
        playback_source=playback_source,
        total_seconds=total_seconds,
        watched_seconds=watched_seconds,
        progress_percent=progress_percent,
        completed=completed,
        rating_value=rating_value,
        rating_scale=rating_scale,
        media_version_id=media_version_id,
        source_event_id=source_event_id,
    )
    session.add(watch_event)
    session.flush()
    session.refresh(watch_event)
    return watch_event


def source_event_exists(
    session: Session,
    *,
    playback_source: str,
    source_event_id: str,
) -> bool:
    statement = select(WatchEvent.watch_id).where(
        WatchEvent.playback_source == playback_source,
        WatchEvent.source_event_id == source_event_id,
    )
    return session.scalar(statement) is not None
