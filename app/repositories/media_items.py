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
