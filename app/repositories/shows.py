from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import Show


def find_show_by_tmdb_id(session: Session, *, tmdb_id: int) -> Show | None:
    statement = select(Show).where(Show.tmdb_id == tmdb_id)
    return session.scalar(statement)


def find_show_by_external_ids(
    session: Session,
    *,
    tmdb_id: int | None,
    tvdb_id: int | None,
    imdb_id: str | None,
) -> Show | None:
    if tmdb_id is not None:
        found = find_show_by_tmdb_id(session, tmdb_id=tmdb_id)
        if found is not None:
            return found

    if tvdb_id is not None:
        statement = select(Show).where(Show.tvdb_id == tvdb_id)
        found = session.scalar(statement)
        if found is not None:
            return found

    if imdb_id:
        statement = select(Show).where(Show.imdb_id == imdb_id)
        found = session.scalar(statement)
        if found is not None:
            return found

    return None


def create_show(
    session: Session,
    *,
    tmdb_id: int,
    title: str,
    year: int | None,
    tvdb_id: int | None,
    imdb_id: str | None,
) -> Show:
    show = Show(
        tmdb_id=tmdb_id,
        title=title,
        year=year,
        tvdb_id=tvdb_id,
        imdb_id=imdb_id,
    )
    session.add(show)
    session.flush()
    session.refresh(show)
    return show
