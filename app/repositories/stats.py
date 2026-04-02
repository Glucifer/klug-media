from decimal import Decimal
from uuid import UUID

from sqlalchemy import Integer, case, cast, func, select
from sqlalchemy.orm import Session

from app.db.models.entities import HorrorfestEntry, MediaItem, MediaVersion, User, WatchEvent


def _effective_runtime_seconds_expr():
    return func.coalesce(
        WatchEvent.watch_runtime_seconds,
        MediaVersion.runtime_seconds,
        WatchEvent.total_seconds,
        MediaItem.base_runtime_seconds,
        0,
    )


def get_summary_stats(
    session: Session,
    *,
    user_id: UUID | None,
) -> dict[str, object]:
    effective_runtime_seconds = _effective_runtime_seconds_expr()
    statement = (
        select(
            func.count(WatchEvent.watch_id),
            func.sum(case((WatchEvent.completed.is_(True), 1), else_=0)),
            func.sum(case((WatchEvent.rewatch.is_(True), 1), else_=0)),
            func.coalesce(func.sum(effective_runtime_seconds), 0),
            func.sum(case((MediaItem.type == "movie", 1), else_=0)),
            func.sum(case((MediaItem.type == "episode", 1), else_=0)),
            func.avg(WatchEvent.rating_value),
            func.sum(
                case(
                    (
                        (WatchEvent.completed.is_(True) & WatchEvent.rating_value.is_(None)),
                        1,
                    ),
                    else_=0,
                )
            ),
        )
        .select_from(WatchEvent)
        .join(User, WatchEvent.user_id == User.user_id)
        .join(MediaItem, WatchEvent.media_item_id == MediaItem.media_item_id)
        .outerjoin(MediaVersion, WatchEvent.media_version_id == MediaVersion.media_version_id)
        .where(WatchEvent.is_deleted.is_(False))
    )
    if user_id is not None:
        statement = statement.where(WatchEvent.user_id == user_id)

    row = session.execute(statement).one()
    total_runtime_seconds = int(row[3] or 0)
    total_runtime_hours = (Decimal(total_runtime_seconds) / Decimal("3600")).quantize(
        Decimal("0.01")
    )
    return {
        "user_id": user_id,
        "total_active_watches": int(row[0] or 0),
        "total_completed_watches": int(row[1] or 0),
        "total_rewatches": int(row[2] or 0),
        "total_watch_time_seconds": total_runtime_seconds,
        "total_watch_time_hours": total_runtime_hours,
        "movie_watch_count": int(row[4] or 0),
        "episode_watch_count": int(row[5] or 0),
        "average_rating_value": row[6],
        "unrated_completed_watch_count": int(row[7] or 0),
    }


def list_monthly_stats(
    session: Session,
    *,
    user_id: UUID | None,
) -> list[dict[str, object]]:
    effective_runtime_seconds = _effective_runtime_seconds_expr()
    local_ts = func.timezone(User.timezone, WatchEvent.watched_at)
    local_year = cast(func.extract("year", local_ts), Integer)
    local_month = cast(func.extract("month", local_ts), Integer)
    statement = (
        select(
            local_year.label("year"),
            local_month.label("month"),
            func.count(WatchEvent.watch_id),
            func.sum(case((MediaItem.type == "movie", 1), else_=0)),
            func.sum(case((MediaItem.type == "episode", 1), else_=0)),
            func.sum(case((WatchEvent.rewatch.is_(True), 1), else_=0)),
            func.sum(case((WatchEvent.rating_value.is_not(None), 1), else_=0)),
            func.coalesce(func.sum(effective_runtime_seconds), 0),
            func.avg(WatchEvent.rating_value),
        )
        .select_from(WatchEvent)
        .join(User, WatchEvent.user_id == User.user_id)
        .join(MediaItem, WatchEvent.media_item_id == MediaItem.media_item_id)
        .outerjoin(MediaVersion, WatchEvent.media_version_id == MediaVersion.media_version_id)
        .where(WatchEvent.is_deleted.is_(False))
        .group_by(local_year, local_month)
        .order_by(local_year.desc(), local_month.desc())
    )
    if user_id is not None:
        statement = statement.where(WatchEvent.user_id == user_id)

    rows = session.execute(statement).all()
    payload: list[dict[str, object]] = []
    for row in rows:
        payload.append(
            {
                "user_id": user_id,
                "year": int(row[0]),
                "month": int(row[1]),
                "watch_count": int(row[2] or 0),
                "movie_count": int(row[3] or 0),
                "episode_count": int(row[4] or 0),
                "rewatch_count": int(row[5] or 0),
                "rated_watch_count": int(row[6] or 0),
                "total_runtime_seconds": int(row[7] or 0),
                "average_rating_value": row[8],
            }
        )
    return payload


def list_horrorfest_stats(
    session: Session,
    *,
    user_id: UUID | None,
) -> list[dict[str, object]]:
    effective_runtime_seconds = _effective_runtime_seconds_expr()
    statement = (
        select(
            HorrorfestEntry.horrorfest_year,
            func.count(HorrorfestEntry.horrorfest_entry_id),
            func.coalesce(func.sum(effective_runtime_seconds), 0),
            func.avg(WatchEvent.rating_value),
            func.sum(case((WatchEvent.rating_value.is_not(None), 1), else_=0)),
            func.sum(case((WatchEvent.rewatch.is_(True), 1), else_=0)),
            func.min(WatchEvent.watched_at),
            func.max(WatchEvent.watched_at),
        )
        .select_from(HorrorfestEntry)
        .join(WatchEvent, WatchEvent.watch_id == HorrorfestEntry.watch_id)
        .join(User, WatchEvent.user_id == User.user_id)
        .join(MediaItem, WatchEvent.media_item_id == MediaItem.media_item_id)
        .outerjoin(MediaVersion, WatchEvent.media_version_id == MediaVersion.media_version_id)
        .where(
            HorrorfestEntry.is_removed.is_(False),
            WatchEvent.is_deleted.is_(False),
        )
        .group_by(HorrorfestEntry.horrorfest_year)
        .order_by(HorrorfestEntry.horrorfest_year.desc())
    )
    if user_id is not None:
        statement = statement.where(WatchEvent.user_id == user_id)

    rows = session.execute(statement).all()
    payload: list[dict[str, object]] = []
    for row in rows:
        total_runtime_seconds = int(row[2] or 0)
        payload.append(
            {
                "user_id": user_id,
                "horrorfest_year": int(row[0]),
                "entry_count": int(row[1] or 0),
                "total_runtime_seconds": total_runtime_seconds,
                "total_runtime_hours": (
                    Decimal(total_runtime_seconds) / Decimal("3600")
                ).quantize(Decimal("0.01")),
                "average_rating_value": row[3],
                "rated_entry_count": int(row[4] or 0),
                "rewatch_count": int(row[5] or 0),
                "first_watch_at": row[6],
                "latest_watch_at": row[7],
            }
        )
    return payload
