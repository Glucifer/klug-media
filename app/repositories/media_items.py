from sqlalchemy import select
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
) -> MediaItem:
    media_item = MediaItem(
        type=media_type,
        title=title,
        year=year,
        tmdb_id=tmdb_id,
        imdb_id=imdb_id,
        tvdb_id=tvdb_id,
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
) -> MediaItem | None:
    if tmdb_id is not None:
        statement = select(MediaItem).where(
            MediaItem.type == media_type,
            MediaItem.tmdb_id == tmdb_id,
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
