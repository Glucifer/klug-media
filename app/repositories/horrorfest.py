from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import Session

from app.db.models.entities import HorrorfestEntry, HorrorfestYear, MediaItem, WatchEvent


def _format_display_title(
    *,
    item_type: str,
    item_title: str | None,
    item_year: int | None,
    season_number: int | None,
    episode_number: int | None,
) -> str:
    base_title = item_title or "Unknown Title"
    if item_type == "episode":
        if season_number is not None and episode_number is not None:
            return f"{base_title} S{season_number:02d}E{episode_number:02d}"
        return base_title
    if item_year is not None:
        return f"{base_title} ({item_year})"
    return base_title


def get_horrorfest_year(
    session: Session,
    *,
    horrorfest_year: int,
) -> HorrorfestYear | None:
    return session.get(HorrorfestYear, horrorfest_year)


def find_overlapping_horrorfest_year(
    session: Session,
    *,
    window_start_at: datetime,
    window_end_at: datetime,
    exclude_year: int | None = None,
) -> HorrorfestYear | None:
    statement = select(HorrorfestYear).where(
        HorrorfestYear.window_start_at <= window_end_at,
        HorrorfestYear.window_end_at >= window_start_at,
    )
    if exclude_year is not None:
        statement = statement.where(HorrorfestYear.horrorfest_year != exclude_year)
    return session.scalar(statement.limit(1))


def create_horrorfest_year(
    session: Session,
    *,
    horrorfest_year: int,
    window_start_at: datetime,
    window_end_at: datetime,
    label: str | None,
    notes: str | None,
    is_active: bool,
    updated_at: datetime | None,
) -> HorrorfestYear:
    row = HorrorfestYear(
        horrorfest_year=horrorfest_year,
        window_start_at=window_start_at,
        window_end_at=window_end_at,
        label=label,
        notes=notes,
        is_active=is_active,
        updated_at=updated_at,
    )
    session.add(row)
    session.flush()
    session.refresh(row)
    return row


def update_horrorfest_year(
    session: Session,
    *,
    year_config: HorrorfestYear,
) -> HorrorfestYear:
    session.add(year_config)
    session.flush()
    session.refresh(year_config)
    return year_config


def list_horrorfest_years(session: Session) -> list[dict[str, object]]:
    effective_runtime = func.coalesce(
        WatchEvent.watch_runtime_seconds,
        WatchEvent.total_seconds,
        MediaItem.base_runtime_seconds,
        0,
    )
    statement = (
        select(
            HorrorfestYear,
            func.count(WatchEvent.watch_id),
            func.coalesce(func.sum(effective_runtime), 0),
            func.avg(WatchEvent.rating_value),
        )
        .outerjoin(
            HorrorfestEntry,
            and_(
                HorrorfestEntry.horrorfest_year == HorrorfestYear.horrorfest_year,
                HorrorfestEntry.is_removed.is_(False),
            ),
        )
        .outerjoin(
            WatchEvent,
            and_(
                WatchEvent.watch_id == HorrorfestEntry.watch_id,
                WatchEvent.is_deleted.is_(False),
            ),
        )
        .outerjoin(MediaItem, MediaItem.media_item_id == WatchEvent.media_item_id)
        .group_by(HorrorfestYear.horrorfest_year)
        .order_by(HorrorfestYear.horrorfest_year.desc())
    )
    rows = session.execute(statement).all()
    payload: list[dict[str, object]] = []
    for year_config, entry_count, total_runtime_seconds, average_rating_value in rows:
        payload.append(
            {
                "horrorfest_year": year_config.horrorfest_year,
                "window_start_at": year_config.window_start_at,
                "window_end_at": year_config.window_end_at,
                "label": year_config.label,
                "notes": year_config.notes,
                "is_active": year_config.is_active,
                "created_at": year_config.created_at,
                "updated_at": year_config.updated_at,
                "entry_count": entry_count or 0,
                "total_runtime_seconds": total_runtime_seconds or 0,
                "average_rating_value": average_rating_value,
            }
        )
    return payload


def list_horrorfest_entries(
    session: Session,
    *,
    horrorfest_year: int,
    include_removed: bool,
) -> list[dict[str, object]]:
    statement: Select[tuple[HorrorfestEntry, WatchEvent, MediaItem]] = (
        select(HorrorfestEntry, WatchEvent, MediaItem)
        .join(WatchEvent, WatchEvent.watch_id == HorrorfestEntry.watch_id)
        .join(MediaItem, MediaItem.media_item_id == WatchEvent.media_item_id)
        .where(HorrorfestEntry.horrorfest_year == horrorfest_year)
    )
    if not include_removed:
        statement = statement.where(HorrorfestEntry.is_removed.is_(False))
    statement = statement.order_by(
        HorrorfestEntry.is_removed.asc(),
        HorrorfestEntry.watch_order.asc().nulls_last(),
        WatchEvent.watched_at.asc(),
        HorrorfestEntry.created_at.asc(),
    )
    rows = session.execute(statement).all()
    payload: list[dict[str, object]] = []
    for entry, watch_event, media_item in rows:
        payload.append(
            {
                "horrorfest_entry_id": entry.horrorfest_entry_id,
                "watch_id": entry.watch_id,
                "horrorfest_year": entry.horrorfest_year,
                "watch_order": entry.watch_order,
                "source_kind": entry.source_kind,
                "created_at": entry.created_at,
                "updated_at": entry.updated_at,
                "updated_by": entry.updated_by,
                "update_reason": entry.update_reason,
                "is_removed": entry.is_removed,
                "removed_at": entry.removed_at,
                "removed_by": entry.removed_by,
                "removed_reason": entry.removed_reason,
                "user_id": watch_event.user_id,
                "media_item_id": watch_event.media_item_id,
                "watched_at": watch_event.watched_at,
                "playback_source": watch_event.playback_source,
                "media_item_title": media_item.title,
                "media_item_type": media_item.type,
                "display_title": _format_display_title(
                    item_type=media_item.type,
                    item_title=media_item.title,
                    item_year=media_item.year,
                    season_number=media_item.season_number,
                    episode_number=media_item.episode_number,
                ),
                "rating_value": watch_event.rating_value,
                "rating_scale": watch_event.rating_scale,
                "effective_runtime_seconds": (
                    watch_event.watch_runtime_seconds
                    or watch_event.total_seconds
                    or media_item.base_runtime_seconds
                ),
                "rewatch": watch_event.rewatch,
                "completed": watch_event.completed,
            }
        )
    return payload


def get_horrorfest_entry(
    session: Session,
    *,
    horrorfest_entry_id: UUID,
) -> HorrorfestEntry | None:
    return session.get(HorrorfestEntry, horrorfest_entry_id)


def get_active_horrorfest_entry_for_watch(
    session: Session,
    *,
    watch_id: UUID,
) -> HorrorfestEntry | None:
    statement = select(HorrorfestEntry).where(
        HorrorfestEntry.watch_id == watch_id,
        HorrorfestEntry.is_removed.is_(False),
    )
    return session.scalar(statement.limit(1))


def get_horrorfest_entry_for_watch_and_year(
    session: Session,
    *,
    watch_id: UUID,
    horrorfest_year: int,
) -> HorrorfestEntry | None:
    statement = select(HorrorfestEntry).where(
        HorrorfestEntry.watch_id == watch_id,
        HorrorfestEntry.horrorfest_year == horrorfest_year,
    )
    return session.scalar(statement.limit(1))


def list_active_horrorfest_entries_for_year(
    session: Session,
    *,
    horrorfest_year: int,
) -> list[HorrorfestEntry]:
    statement = (
        select(HorrorfestEntry)
        .where(
            HorrorfestEntry.horrorfest_year == horrorfest_year,
            HorrorfestEntry.is_removed.is_(False),
        )
        .order_by(
            HorrorfestEntry.watch_order.asc().nulls_last(),
            HorrorfestEntry.created_at.asc(),
            HorrorfestEntry.horrorfest_entry_id.asc(),
        )
    )
    return list(session.scalars(statement))


def find_horrorfest_year_for_timestamp(
    session: Session,
    *,
    watched_at: datetime,
) -> HorrorfestYear | None:
    statement = (
        select(HorrorfestYear)
        .where(
            HorrorfestYear.is_active.is_(True),
            HorrorfestYear.window_start_at <= watched_at,
            HorrorfestYear.window_end_at >= watched_at,
        )
        .order_by(HorrorfestYear.horrorfest_year.desc())
    )
    return session.scalar(statement.limit(1))


def create_horrorfest_entry(
    session: Session,
    *,
    watch_id: UUID,
    horrorfest_year: int,
    watch_order: int | None,
    source_kind: str,
    updated_at: datetime | None = None,
    updated_by: str | None = None,
    update_reason: str | None = None,
) -> HorrorfestEntry:
    row = HorrorfestEntry(
        watch_id=watch_id,
        horrorfest_year=horrorfest_year,
        watch_order=watch_order,
        source_kind=source_kind,
        updated_at=updated_at,
        updated_by=updated_by,
        update_reason=update_reason,
    )
    session.add(row)
    session.flush()
    session.refresh(row)
    return row


def update_horrorfest_entry(
    session: Session,
    *,
    entry: HorrorfestEntry,
) -> HorrorfestEntry:
    session.add(entry)
    session.flush()
    session.refresh(entry)
    return entry
