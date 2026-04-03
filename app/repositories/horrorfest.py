from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, Integer, Select, and_, case, cast, func, select
from sqlalchemy.orm import Session

from app.db.models.entities import (
    HorrorfestEntry,
    HorrorfestYear,
    MediaItem,
    MediaVersion,
    User,
    WatchEvent,
)


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


def _effective_runtime_expr():
    return func.coalesce(
        WatchEvent.watch_runtime_seconds,
        MediaVersion.runtime_seconds,
        WatchEvent.total_seconds,
        MediaItem.base_runtime_seconds,
        0,
    )


def _horrorfest_analytics_base_statement(
    *,
    horrorfest_year: int | None = None,
    user_id: UUID | None = None,
) -> Select:
    local_ts = func.timezone(User.timezone, WatchEvent.watched_at)
    local_date = cast(local_ts, Date)
    statement = (
        select(
            HorrorfestEntry.horrorfest_year.label("horrorfest_year"),
            local_date.label("watch_date"),
            WatchEvent.playback_source.label("playback_source"),
            WatchEvent.rating_value.label("rating_value"),
            WatchEvent.watched_at.label("watched_at"),
            WatchEvent.rewatch.label("rewatch"),
            MediaItem.media_item_id.label("media_item_id"),
            MediaItem.title.label("media_item_title"),
            MediaItem.year.label("media_item_year"),
            _effective_runtime_expr().label("effective_runtime_seconds"),
        )
        .select_from(HorrorfestEntry)
        .join(WatchEvent, WatchEvent.watch_id == HorrorfestEntry.watch_id)
        .join(User, User.user_id == WatchEvent.user_id)
        .join(MediaItem, MediaItem.media_item_id == WatchEvent.media_item_id)
        .outerjoin(MediaVersion, MediaVersion.media_version_id == WatchEvent.media_version_id)
        .where(
            HorrorfestEntry.is_removed.is_(False),
            WatchEvent.is_deleted.is_(False),
        )
    )
    if horrorfest_year is not None:
        statement = statement.where(HorrorfestEntry.horrorfest_year == horrorfest_year)
    if user_id is not None:
        statement = statement.where(WatchEvent.user_id == user_id)
    return statement


def _build_analytics_summary(row: object) -> dict[str, object]:
    watch_count = int(row.watch_count or 0)
    watch_days = int(row.watch_days or 0)
    total_runtime_seconds = int(row.total_runtime_seconds or 0)
    watch_count_decimal = Decimal(watch_count or 1)
    watch_days_decimal = Decimal(watch_days or 1)
    return {
        "horrorfest_year": int(row.horrorfest_year),
        "watch_count": watch_count,
        "watch_days": watch_days,
        "new_watch_count": int(row.new_watch_count or 0),
        "rewatch_count": int(row.rewatch_count or 0),
        "total_runtime_seconds": total_runtime_seconds,
        "total_runtime_hours": (
            Decimal(total_runtime_seconds) / Decimal("3600")
        ).quantize(Decimal("0.01")),
        "average_watches_per_day": (
            Decimal(watch_count) / watch_days_decimal
        ).quantize(Decimal("0.01")),
        "average_runtime_hours_per_day": (
            Decimal(total_runtime_seconds) / Decimal("3600") / watch_days_decimal
        ).quantize(Decimal("0.01")),
        "average_runtime_minutes_per_watch": (
            Decimal(total_runtime_seconds) / Decimal("60") / watch_count_decimal
        ).quantize(Decimal("0.01")),
        "average_rating_value": row.average_rating_value,
        "rated_watch_count": int(row.rated_watch_count or 0),
        "first_watch_at": row.first_watch_at,
        "latest_watch_at": row.latest_watch_at,
    }


def _build_cross_year_matrix(
    rows: list[object],
    *,
    label_key: str,
    extra_key: str | None = None,
    media_item_key: str | None = None,
    row_label_name: str,
) -> dict[str, object]:
    years = sorted({int(row.horrorfest_year) for row in rows}, reverse=True)
    grouped: dict[tuple[object, ...], dict[str, object]] = {}
    for row in rows:
        label_value = getattr(row, label_key)
        extra_value = getattr(row, extra_key) if extra_key else None
        group_key = (label_value, extra_value)
        if group_key not in grouped:
            if extra_key and extra_value is not None and row_label_name == "title":
                display_label = f"{label_value} ({extra_value})"
            else:
                display_label = str(label_value)
            grouped[group_key] = {
                row_label_name: display_label,
                "total_count": 0,
                "year_counts": {str(year): 0 for year in years},
            }
            if media_item_key:
                grouped[group_key]["media_item_id"] = getattr(row, media_item_key)
        grouped[group_key]["total_count"] += int(row.watch_count or 0)
        grouped[group_key]["year_counts"][str(int(row.horrorfest_year))] = int(
            row.watch_count or 0
        )

    def _sort_key(item: dict[str, object]) -> tuple[object, ...]:
        label = str(item[row_label_name]).lower()
        return (label,)

    return {
        "years": years,
        "rows": sorted(grouped.values(), key=_sort_key),
    }


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


def list_horrorfest_analytics_years(
    session: Session,
    *,
    user_id: UUID | None = None,
) -> list[dict[str, object]]:
    analytics_rows = _horrorfest_analytics_base_statement(user_id=user_id).subquery()
    statement = (
        select(
            analytics_rows.c.horrorfest_year,
            func.count().label("watch_count"),
            func.count(func.distinct(analytics_rows.c.watch_date)).label("watch_days"),
            func.sum(case((analytics_rows.c.rewatch.is_(False), 1), else_=0)).label(
                "new_watch_count"
            ),
            func.sum(case((analytics_rows.c.rewatch.is_(True), 1), else_=0)).label(
                "rewatch_count"
            ),
            func.coalesce(func.sum(analytics_rows.c.effective_runtime_seconds), 0).label(
                "total_runtime_seconds"
            ),
            func.avg(analytics_rows.c.rating_value).label("average_rating_value"),
            func.sum(
                case((analytics_rows.c.rating_value.is_not(None), 1), else_=0)
            ).label("rated_watch_count"),
            func.min(analytics_rows.c.watched_at).label("first_watch_at"),
            func.max(analytics_rows.c.watched_at).label("latest_watch_at"),
        )
        .group_by(analytics_rows.c.horrorfest_year)
        .order_by(analytics_rows.c.horrorfest_year.desc())
    )
    rows = session.execute(statement).all()
    return [_build_analytics_summary(row) for row in rows]


def list_horrorfest_analytics_title_matrix(
    session: Session,
    *,
    user_id: UUID | None = None,
) -> dict[str, object]:
    analytics_rows = _horrorfest_analytics_base_statement(user_id=user_id).subquery()
    statement = (
        select(
            analytics_rows.c.media_item_id,
            analytics_rows.c.media_item_title,
            analytics_rows.c.media_item_year,
            analytics_rows.c.horrorfest_year,
            func.count().label("watch_count"),
        )
        .group_by(
            analytics_rows.c.media_item_id,
            analytics_rows.c.media_item_title,
            analytics_rows.c.media_item_year,
            analytics_rows.c.horrorfest_year,
        )
        .order_by(
            analytics_rows.c.media_item_title.asc(),
            analytics_rows.c.media_item_year.asc().nulls_last(),
            analytics_rows.c.horrorfest_year.desc(),
        )
    )
    rows = session.execute(statement).all()
    return _build_cross_year_matrix(
        rows,
        label_key="media_item_title",
        extra_key="media_item_year",
        media_item_key="media_item_id",
        row_label_name="title",
    )


def list_horrorfest_analytics_decade_matrix(
    session: Session,
    *,
    user_id: UUID | None = None,
) -> dict[str, object]:
    analytics_rows = _horrorfest_analytics_base_statement(user_id=user_id).subquery()
    decade_start = cast((analytics_rows.c.media_item_year / 10), Integer) * 10
    decade_label = func.concat(decade_start, "s")
    statement = (
        select(
            decade_start.label("decade_start"),
            decade_label.label("decade"),
            analytics_rows.c.horrorfest_year,
            func.count().label("watch_count"),
        )
        .where(analytics_rows.c.media_item_year.is_not(None))
        .group_by(decade_start, decade_label, analytics_rows.c.horrorfest_year)
        .order_by(decade_start.asc(), analytics_rows.c.horrorfest_year.desc())
    )
    rows = session.execute(statement).all()
    years = sorted({int(row.horrorfest_year) for row in rows}, reverse=True)
    grouped: dict[int, dict[str, object]] = {}
    for row in rows:
        decade_key = int(row.decade_start)
        if decade_key not in grouped:
            grouped[decade_key] = {
                "decade": str(row.decade),
                "total_count": 0,
                "year_counts": {str(year): 0 for year in years},
            }
        grouped[decade_key]["total_count"] += int(row.watch_count or 0)
        grouped[decade_key]["year_counts"][str(int(row.horrorfest_year))] = int(
            row.watch_count or 0
        )
    return {
        "years": years,
        "rows": [grouped[key] for key in sorted(grouped.keys())],
    }


def get_horrorfest_analytics_year_detail(
    session: Session,
    *,
    horrorfest_year: int,
    user_id: UUID | None = None,
) -> dict[str, object] | None:
    analytics_rows = _horrorfest_analytics_base_statement(
        horrorfest_year=horrorfest_year,
        user_id=user_id,
    ).subquery()
    summary_statement = select(
        analytics_rows.c.horrorfest_year,
        func.count().label("watch_count"),
        func.count(func.distinct(analytics_rows.c.watch_date)).label("watch_days"),
        func.sum(case((analytics_rows.c.rewatch.is_(False), 1), else_=0)).label(
            "new_watch_count"
        ),
        func.sum(case((analytics_rows.c.rewatch.is_(True), 1), else_=0)).label(
            "rewatch_count"
        ),
        func.coalesce(func.sum(analytics_rows.c.effective_runtime_seconds), 0).label(
            "total_runtime_seconds"
        ),
        func.avg(analytics_rows.c.rating_value).label("average_rating_value"),
        func.sum(case((analytics_rows.c.rating_value.is_not(None), 1), else_=0)).label(
            "rated_watch_count"
        ),
        func.min(analytics_rows.c.watched_at).label("first_watch_at"),
        func.max(analytics_rows.c.watched_at).label("latest_watch_at"),
    ).group_by(analytics_rows.c.horrorfest_year)
    summary_row = session.execute(summary_statement).one_or_none()
    if summary_row is None:
        return None

    daily_statement = (
        select(
            analytics_rows.c.watch_date,
            func.count().label("watch_count"),
            func.coalesce(func.sum(analytics_rows.c.effective_runtime_seconds), 0).label(
                "total_runtime_seconds"
            ),
            func.avg(analytics_rows.c.rating_value).label("average_rating_value"),
        )
        .group_by(analytics_rows.c.watch_date)
        .order_by(analytics_rows.c.watch_date.asc())
    )
    source_statement = (
        select(
            analytics_rows.c.playback_source,
            func.count().label("watch_count"),
            func.coalesce(func.sum(analytics_rows.c.effective_runtime_seconds), 0).label(
                "total_runtime_seconds"
            ),
            func.avg(analytics_rows.c.rating_value).label("average_rating_value"),
        )
        .group_by(analytics_rows.c.playback_source)
        .order_by(func.count().desc(), analytics_rows.c.playback_source.asc())
    )
    rating_statement = (
        select(
            analytics_rows.c.rating_value,
            func.count().label("watch_count"),
        )
        .where(analytics_rows.c.rating_value.is_not(None))
        .group_by(analytics_rows.c.rating_value)
        .order_by(analytics_rows.c.rating_value.desc())
    )

    daily_rows = session.execute(daily_statement).all()
    source_rows = session.execute(source_statement).all()
    rating_rows = session.execute(rating_statement).all()
    return {
        "summary": _build_analytics_summary(summary_row),
        "daily_rows": [
            {
                "watch_date": row.watch_date,
                "watch_count": int(row.watch_count or 0),
                "total_runtime_seconds": int(row.total_runtime_seconds or 0),
                "total_runtime_hours": (
                    Decimal(int(row.total_runtime_seconds or 0)) / Decimal("3600")
                ).quantize(Decimal("0.01")),
                "average_rating_value": row.average_rating_value,
            }
            for row in daily_rows
        ],
        "source_rows": [
            {
                "playback_source": row.playback_source,
                "watch_count": int(row.watch_count or 0),
                "total_runtime_seconds": int(row.total_runtime_seconds or 0),
                "total_runtime_hours": (
                    Decimal(int(row.total_runtime_seconds or 0)) / Decimal("3600")
                ).quantize(Decimal("0.01")),
                "average_rating_value": row.average_rating_value,
            }
            for row in source_rows
        ],
        "rating_rows": [
            {
                "rating_value": row.rating_value,
                "watch_count": int(row.watch_count or 0),
            }
            for row in rating_rows
        ],
    }


def _build_horrorfest_entry_payload(
    entry: HorrorfestEntry,
    watch_event: WatchEvent,
    media_item: MediaItem,
) -> dict[str, object]:
    return {
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


def _list_horrorfest_entry_rows(
    session: Session,
    *,
    include_removed: bool = False,
    user_id: UUID | None = None,
    horrorfest_year: int | None = None,
    media_item_id: UUID | None = None,
    decade_start: int | None = None,
) -> list[dict[str, object]]:
    statement: Select[tuple[HorrorfestEntry, WatchEvent, MediaItem]] = (
        select(HorrorfestEntry, WatchEvent, MediaItem)
        .join(WatchEvent, WatchEvent.watch_id == HorrorfestEntry.watch_id)
        .join(MediaItem, MediaItem.media_item_id == WatchEvent.media_item_id)
    )
    if not include_removed:
        statement = statement.where(
            HorrorfestEntry.is_removed.is_(False),
            WatchEvent.is_deleted.is_(False),
        )
    if user_id is not None:
        statement = statement.where(WatchEvent.user_id == user_id)
    if horrorfest_year is not None:
        statement = statement.where(HorrorfestEntry.horrorfest_year == horrorfest_year)
    if media_item_id is not None:
        statement = statement.where(MediaItem.media_item_id == media_item_id)
    if decade_start is not None:
        statement = statement.where(
            MediaItem.year.is_not(None),
            MediaItem.year >= decade_start,
            MediaItem.year < decade_start + 10,
        )
    statement = statement.order_by(
        HorrorfestEntry.horrorfest_year.desc(),
        HorrorfestEntry.watch_order.asc().nulls_last(),
        WatchEvent.watched_at.asc(),
        HorrorfestEntry.created_at.asc(),
    )
    rows = session.execute(statement).all()
    return [
        _build_horrorfest_entry_payload(entry, watch_event, media_item)
        for entry, watch_event, media_item in rows
    ]


def list_horrorfest_entries(
    session: Session,
    *,
    horrorfest_year: int,
    include_removed: bool,
) -> list[dict[str, object]]:
    return _list_horrorfest_entry_rows(
        session,
        horrorfest_year=horrorfest_year,
        include_removed=include_removed,
    )


def list_horrorfest_title_entries(
    session: Session,
    *,
    media_item_id: UUID,
    horrorfest_year: int | None = None,
    user_id: UUID | None = None,
) -> list[dict[str, object]]:
    return _list_horrorfest_entry_rows(
        session,
        user_id=user_id,
        horrorfest_year=horrorfest_year,
        media_item_id=media_item_id,
    )


def list_horrorfest_decade_entries(
    session: Session,
    *,
    decade_start: int,
    horrorfest_year: int | None = None,
    user_id: UUID | None = None,
) -> list[dict[str, object]]:
    return _list_horrorfest_entry_rows(
        session,
        user_id=user_id,
        horrorfest_year=horrorfest_year,
        decade_start=decade_start,
    )


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
