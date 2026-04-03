from __future__ import annotations

from sqlalchemy import Select, String, and_, case, cast, distinct, func, select
from sqlalchemy.orm import Session

from app.db.models.entities import HorrorfestEntry, MediaItem, Show, WatchEvent


def _latest_rating_subquery() -> Select:
    ranked = (
        select(
            WatchEvent.media_item_id.label("media_item_id"),
            WatchEvent.rating_value.label("rating_value"),
            WatchEvent.rating_scale.label("rating_scale"),
            func.row_number()
            .over(
                partition_by=WatchEvent.media_item_id,
                order_by=(WatchEvent.watched_at.desc(), WatchEvent.created_at.desc()),
            )
            .label("rating_rank"),
        )
        .where(
            WatchEvent.is_deleted.is_(False),
            WatchEvent.rating_value.is_not(None),
        )
        .subquery()
    )
    return select(
        ranked.c.media_item_id,
        ranked.c.rating_value,
        ranked.c.rating_scale,
    ).where(ranked.c.rating_rank == 1)


def _watch_stats_subquery() -> Select:
    return (
        select(
            WatchEvent.media_item_id.label("media_item_id"),
            func.count(WatchEvent.watch_id).label("watch_count"),
            func.max(WatchEvent.watched_at).label("latest_watched_at"),
        )
        .where(WatchEvent.is_deleted.is_(False))
        .group_by(WatchEvent.media_item_id)
    )


def _horrorfest_stats_subquery() -> Select:
    return (
        select(
            WatchEvent.media_item_id.label("media_item_id"),
            func.max(HorrorfestEntry.horrorfest_year).label("horrorfest_year"),
        )
        .join(HorrorfestEntry, HorrorfestEntry.watch_id == WatchEvent.watch_id)
        .where(
            WatchEvent.is_deleted.is_(False),
            HorrorfestEntry.is_removed.is_(False),
        )
        .group_by(WatchEvent.media_item_id)
    )


def list_library_movies(
    session: Session,
    *,
    query: str | None,
    watched: bool | None,
    enrichment_status: str | None,
    year: int | None,
    limit: int,
    offset: int,
) -> list[dict]:
    if watched is False:
        return []

    watch_stats = _watch_stats_subquery().subquery()
    latest_rating = _latest_rating_subquery().subquery()
    horrorfest_stats = _horrorfest_stats_subquery().subquery()

    statement = (
        select(
            MediaItem.media_item_id,
            MediaItem.title,
            MediaItem.year,
            watch_stats.c.watch_count,
            watch_stats.c.latest_watched_at,
            latest_rating.c.rating_value.label("latest_rating_value"),
            latest_rating.c.rating_scale.label("latest_rating_scale"),
            MediaItem.enrichment_status,
            horrorfest_stats.c.horrorfest_year,
        )
        .join(watch_stats, watch_stats.c.media_item_id == MediaItem.media_item_id)
        .outerjoin(
            latest_rating,
            latest_rating.c.media_item_id == MediaItem.media_item_id,
        )
        .outerjoin(
            horrorfest_stats,
            horrorfest_stats.c.media_item_id == MediaItem.media_item_id,
        )
        .where(MediaItem.type == "movie")
    )

    if query:
        statement = statement.where(MediaItem.title.ilike(f"%{query}%"))
    if enrichment_status:
        statement = statement.where(MediaItem.enrichment_status == enrichment_status)
    if year is not None:
        statement = statement.where(MediaItem.year == year)

    statement = statement.order_by(
        watch_stats.c.latest_watched_at.desc(),
        MediaItem.title.asc(),
    ).offset(offset).limit(limit)

    rows = session.execute(statement).mappings().all()
    return [dict(row) for row in rows]


def list_library_episodes(
    session: Session,
    *,
    query: str | None,
    show_query: str | None,
    watched: bool | None,
    enrichment_status: str | None,
    limit: int,
    offset: int,
) -> list[dict]:
    if watched is False:
        return []

    watch_stats = _watch_stats_subquery().subquery()
    horrorfest_stats = _horrorfest_stats_subquery().subquery()

    statement = (
        select(
            MediaItem.media_item_id,
            MediaItem.show_id,
            Show.title.label("show_title"),
            MediaItem.season_number,
            MediaItem.episode_number,
            MediaItem.title,
            watch_stats.c.watch_count,
            watch_stats.c.latest_watched_at,
            MediaItem.enrichment_status,
            horrorfest_stats.c.horrorfest_year,
        )
        .join(watch_stats, watch_stats.c.media_item_id == MediaItem.media_item_id)
        .outerjoin(Show, Show.show_id == MediaItem.show_id)
        .outerjoin(
            horrorfest_stats,
            horrorfest_stats.c.media_item_id == MediaItem.media_item_id,
        )
        .where(MediaItem.type == "episode")
    )

    if query:
        pattern = f"%{query}%"
        statement = statement.where(
            (MediaItem.title.ilike(pattern)) | (Show.title.ilike(pattern))
        )
    if show_query:
        statement = statement.where(Show.title.ilike(f"%{show_query}%"))
    if enrichment_status:
        statement = statement.where(MediaItem.enrichment_status == enrichment_status)

    statement = statement.order_by(
        Show.title.asc().nulls_last(),
        MediaItem.season_number.asc().nulls_last(),
        MediaItem.episode_number.asc().nulls_last(),
        MediaItem.title.asc(),
    ).offset(offset).limit(limit)

    rows = session.execute(statement).mappings().all()
    return [dict(row) for row in rows]


def list_library_shows(
    session: Session,
    *,
    query: str | None,
    watched: bool | None,
    limit: int,
    offset: int,
) -> list[dict]:
    watched_episode_case = case(
        (WatchEvent.completed.is_(True), MediaItem.media_item_id),
        else_=None,
    )
    show_media_subquery = (
        select(
            MediaItem.show_id.label("show_id"),
            func.min(cast(MediaItem.media_item_id, String)).label("media_item_id"),
        )
        .where(
            MediaItem.type == "show",
            MediaItem.show_id.is_not(None),
        )
        .group_by(MediaItem.show_id)
        .subquery()
    )

    statement = (
        select(
            Show.show_id,
            show_media_subquery.c.media_item_id,
            Show.title,
            Show.year,
            func.count(distinct(MediaItem.media_item_id)).label("total_episodes"),
            func.count(distinct(watched_episode_case)).label("watched_episodes"),
        )
        .join(
            MediaItem,
            and_(MediaItem.show_id == Show.show_id, MediaItem.type == "episode"),
        )
        .outerjoin(
            WatchEvent,
            and_(
                WatchEvent.media_item_id == MediaItem.media_item_id,
                WatchEvent.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            show_media_subquery,
            show_media_subquery.c.show_id == Show.show_id,
        )
        .group_by(Show.show_id, show_media_subquery.c.media_item_id, Show.title, Show.year)
        .having(func.count(distinct(watched_episode_case)) > 0)
    )

    if watched is False:
        return []
    if query:
        statement = statement.where(Show.title.ilike(f"%{query}%"))

    statement = statement.order_by(
        func.count(distinct(watched_episode_case)).desc(),
        Show.title.asc(),
    ).offset(offset).limit(limit)

    rows = session.execute(statement).mappings().all()
    payload: list[dict] = []
    for row in rows:
        watched_episodes = int(row["watched_episodes"] or 0)
        total_episodes = int(row["total_episodes"] or 0)
        watched_percent = (
            round((watched_episodes / total_episodes) * 100, 2)
            if total_episodes
            else 0
        )
        payload.append(
            {
                "show_id": row["show_id"],
                "media_item_id": row["media_item_id"],
                "title": row["title"],
                "year": row["year"],
                "watched_episodes": watched_episodes,
                "total_episodes": total_episodes,
                "watched_percent": watched_percent,
            }
        )
    return payload
