from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models.entities import MediaItem


def list_media_items(session: Session) -> list[MediaItem]:
    statement = select(MediaItem).order_by(MediaItem.created_at.desc())
    return list(session.scalars(statement))


def create_media_item(
    session: Session,
    *,
    media_type: str,
    title: str,
    year: int | None,
    tmdb_id: int | None,
    imdb_id: str | None,
    tvdb_id: int | None,
    show_tmdb_id: int | None = None,
    season_number: int | None = None,
    episode_number: int | None = None,
    show_id=None,
    summary: str | None = None,
    poster_url: str | None = None,
    release_date=None,
    base_runtime_seconds: int | None = None,
    metadata_source: str | None = None,
    metadata_updated_at: datetime | None = None,
    enrichment_status: str = "pending",
    enrichment_error: str | None = None,
    enrichment_attempted_at: datetime | None = None,
) -> MediaItem:
    media_item = MediaItem(
        type=media_type,
        title=title,
        year=year,
        summary=summary,
        poster_url=poster_url,
        release_date=release_date,
        tmdb_id=tmdb_id,
        imdb_id=imdb_id,
        tvdb_id=tvdb_id,
        show_tmdb_id=show_tmdb_id,
        season_number=season_number,
        episode_number=episode_number,
        show_id=show_id,
        base_runtime_seconds=base_runtime_seconds,
        metadata_source=metadata_source,
        metadata_updated_at=metadata_updated_at,
        enrichment_status=enrichment_status,
        enrichment_error=enrichment_error,
        enrichment_attempted_at=enrichment_attempted_at,
    )
    session.add(media_item)
    session.flush()
    session.refresh(media_item)
    return media_item


def find_media_item_by_external_ids(
    session: Session,
    *,
    media_type: str,
    tmdb_id: int | None,
    imdb_id: str | None,
    tvdb_id: int | None = None,
) -> MediaItem | None:
    if tmdb_id is not None:
        statement = select(MediaItem).where(
            MediaItem.type == media_type,
            MediaItem.tmdb_id == tmdb_id,
        )
        found = session.scalar(statement)
        if found is not None:
            return found

    if tvdb_id is not None:
        statement = select(MediaItem).where(
            MediaItem.type == media_type,
            MediaItem.tvdb_id == tvdb_id,
        )
        found = session.scalar(statement)
        if found is not None:
            return found

    if imdb_id:
        statement = select(MediaItem).where(
            MediaItem.type == media_type,
            MediaItem.imdb_id == imdb_id,
        )
        found = session.scalar(statement)
        if found is not None:
            return found

    return None


def find_episode_media_item(
    session: Session,
    *,
    show_tmdb_id: int,
    season_number: int,
    episode_number: int,
) -> MediaItem | None:
    statement = select(MediaItem).where(
        MediaItem.type == "episode",
        MediaItem.show_tmdb_id == show_tmdb_id,
        MediaItem.season_number == season_number,
        MediaItem.episode_number == episode_number,
    )
    return session.scalar(statement)


def list_episode_media_items_missing_show_id(
    session: Session, *, limit: int | None
) -> list[MediaItem]:
    statement = (
        select(MediaItem)
        .where(
            MediaItem.type == "episode",
            MediaItem.show_tmdb_id.is_not(None),
            MediaItem.show_id.is_(None),
        )
        .order_by(MediaItem.created_at.asc())
    )
    if limit is not None:
        statement = statement.limit(limit)
    return list(session.scalars(statement))


def find_show_media_item_by_tmdb_id(
    session: Session, *, show_tmdb_id: int
) -> MediaItem | None:
    statement = select(MediaItem).where(
        MediaItem.type == "show",
        MediaItem.tmdb_id == show_tmdb_id,
    )
    return session.scalar(statement)


def get_media_item(session: Session, *, media_item_id) -> MediaItem | None:
    statement = select(MediaItem).where(MediaItem.media_item_id == media_item_id)
    return session.scalar(statement)


def list_media_items_for_enrichment(
    session: Session,
    *,
    enrichment_status: str | None,
    missing_ids_only: bool,
    limit: int,
    offset: int,
) -> list[MediaItem]:
    statement = select(MediaItem)
    if enrichment_status:
        statement = statement.where(MediaItem.enrichment_status == enrichment_status)
    if missing_ids_only:
        statement = statement.where(
            MediaItem.tmdb_id.is_(None),
            or_(MediaItem.imdb_id.is_(None), MediaItem.tvdb_id.is_(None)),
        )
    statement = statement.order_by(MediaItem.created_at.desc()).limit(limit).offset(offset)
    return list(session.scalars(statement))


def update_media_item(
    session: Session,
    *,
    media_item: MediaItem,
    title: str | None = None,
    year: int | None = None,
    summary: str | None = None,
    poster_url: str | None = None,
    release_date=None,
    tmdb_id: int | None = None,
    imdb_id: str | None = None,
    tvdb_id: int | None = None,
    show_tmdb_id: int | None = None,
    show_id=None,
    base_runtime_seconds: int | None = None,
    metadata_source: str | None = None,
    metadata_updated_at: datetime | None = None,
    enrichment_status: str | None = None,
    enrichment_error: str | None = None,
    enrichment_attempted_at: datetime | None = None,
) -> MediaItem:
    if title is not None:
        media_item.title = title
    if year is not None:
        media_item.year = year
    media_item.summary = summary
    media_item.poster_url = poster_url
    media_item.release_date = release_date
    if tmdb_id is not None:
        media_item.tmdb_id = tmdb_id
    if imdb_id is not None:
        media_item.imdb_id = imdb_id
    if tvdb_id is not None:
        media_item.tvdb_id = tvdb_id
    if show_tmdb_id is not None:
        media_item.show_tmdb_id = show_tmdb_id
    media_item.show_id = show_id
    media_item.base_runtime_seconds = base_runtime_seconds
    media_item.metadata_source = metadata_source
    media_item.metadata_updated_at = metadata_updated_at
    if enrichment_status is not None:
        media_item.enrichment_status = enrichment_status
    media_item.enrichment_error = enrichment_error
    media_item.enrichment_attempted_at = enrichment_attempted_at
    session.add(media_item)
    session.flush()
    session.refresh(media_item)
    return media_item


def mark_media_item_enrichment(
    session: Session,
    *,
    media_item: MediaItem,
    enrichment_status: str,
    enrichment_error: str | None,
) -> MediaItem:
    media_item.enrichment_status = enrichment_status
    media_item.enrichment_error = enrichment_error
    media_item.enrichment_attempted_at = datetime.now(UTC)
    session.add(media_item)
    session.flush()
    session.refresh(media_item)
    return media_item


def record_media_item_enrichment_attempt(
    session: Session,
    *,
    media_item: MediaItem,
    enrichment_status: str,
    enrichment_error: str | None,
    enrichment_attempted_at: datetime,
) -> MediaItem:
    media_item.enrichment_status = enrichment_status
    media_item.enrichment_error = enrichment_error
    media_item.enrichment_attempted_at = enrichment_attempted_at
    session.add(media_item)
    session.flush()
    session.refresh(media_item)
    return media_item
