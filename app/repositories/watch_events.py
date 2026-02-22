from datetime import date, datetime
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.models.entities import MediaItem, Show, User, WatchEvent


def _format_display_title(
    *,
    item_type: str,
    item_title: str | None,
    item_year: int | None,
    show_title: str | None,
    season_number: int | None,
    episode_number: int | None,
) -> str:
    base_title = item_title or "Unknown Title"
    if item_type == "episode":
        episode_show_title = show_title or base_title
        if season_number is not None and episode_number is not None:
            return f"{episode_show_title} S{season_number:02d}E{episode_number:02d}"
        return episode_show_title

    if item_year is not None:
        return f"{base_title} ({item_year})"
    return base_title


def list_watch_events(
    session: Session,
    *,
    user_id: UUID | None,
    media_item_id: UUID | None,
    watched_after: datetime | None,
    watched_before: datetime | None,
    local_date_from: date | None,
    local_date_to: date | None,
    media_type: Literal["movie", "show", "episode"] | None,
    limit: int,
    offset: int,
) -> list[dict[str, object]]:
    statement: Select[
        tuple[
            WatchEvent,
            str,
            str,
            int | None,
            int | None,
            int | None,
            str | None,
            str,
        ]
    ] = (
        select(
            WatchEvent,
            MediaItem.title,
            MediaItem.type,
            MediaItem.season_number,
            MediaItem.episode_number,
            MediaItem.year,
            Show.title,
            User.timezone,
        )
        .join(User, WatchEvent.user_id == User.user_id)
        .join(
            MediaItem,
            WatchEvent.media_item_id == MediaItem.media_item_id,
        )
        .outerjoin(
            Show,
            MediaItem.show_id == Show.show_id,
        )
    )
    if media_type is not None:
        statement = statement.where(MediaItem.type == media_type)

    if user_id is not None:
        statement = statement.where(WatchEvent.user_id == user_id)
    if media_item_id is not None:
        statement = statement.where(WatchEvent.media_item_id == media_item_id)
    if watched_after is not None:
        statement = statement.where(WatchEvent.watched_at >= watched_after)
    if watched_before is not None:
        statement = statement.where(WatchEvent.watched_at <= watched_before)
    local_watch_date = func.date(func.timezone(User.timezone, WatchEvent.watched_at))
    if local_date_from is not None:
        statement = statement.where(local_watch_date >= local_date_from)
    if local_date_to is not None:
        statement = statement.where(local_watch_date <= local_date_to)

    statement = (
        statement.order_by(WatchEvent.watched_at.desc()).offset(offset).limit(limit)
    )
    rows = session.execute(statement).all()
    payload: list[dict[str, object]] = []
    for (
        watch_event,
        item_title,
        item_type,
        season_number,
        episode_number,
        item_year,
        show_title,
        user_timezone,
    ) in rows:
        normalized_user_timezone = user_timezone or "UTC"
        try:
            watched_at_local = watch_event.watched_at.astimezone(
                ZoneInfo(normalized_user_timezone)
            )
        except ZoneInfoNotFoundError:
            watched_at_local = watch_event.watched_at
        payload.append(
            {
                "watch_id": watch_event.watch_id,
                "user_id": watch_event.user_id,
                "media_item_id": watch_event.media_item_id,
                "watched_at": watch_event.watched_at,
                "playback_source": watch_event.playback_source,
                "total_seconds": watch_event.total_seconds,
                "watched_seconds": watch_event.watched_seconds,
                "progress_percent": watch_event.progress_percent,
                "completed": watch_event.completed,
                "rating_value": watch_event.rating_value,
                "rating_scale": watch_event.rating_scale,
                "media_version_id": watch_event.media_version_id,
                "import_batch_id": watch_event.import_batch_id,
                "created_at": watch_event.created_at,
                "rewatch": watch_event.rewatch,
                "dedupe_hash": watch_event.dedupe_hash,
                "created_by": watch_event.created_by,
                "source_event_id": watch_event.source_event_id,
                "media_item_title": item_title,
                "media_item_type": item_type,
                "media_item_season_number": season_number,
                "media_item_episode_number": episode_number,
                "display_title": _format_display_title(
                    item_type=item_type,
                    item_title=item_title,
                    item_year=item_year,
                    show_title=show_title,
                    season_number=season_number,
                    episode_number=episode_number,
                ),
                "watched_at_local": watched_at_local,
                "user_timezone": normalized_user_timezone,
            }
        )
    return payload


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
