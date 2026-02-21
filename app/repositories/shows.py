from uuid import UUID

from sqlalchemy import select, text
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


def list_shows(session: Session) -> list[Show]:
    statement = select(Show).order_by(Show.title.asc(), Show.created_at.asc())
    return list(session.scalars(statement))


def find_show_by_id(session: Session, *, show_id: UUID) -> Show | None:
    statement = select(Show).where(Show.show_id == show_id)
    return session.scalar(statement)


def list_show_progress(
    session: Session,
    *,
    user_id: UUID | None,
    show_id: UUID | None = None,
) -> list[dict]:
    statement = """
        SELECT
            show_id,
            show_tmdb_id,
            show_title,
            user_id,
            total_episodes,
            watched_episodes,
            watched_percent
        FROM app.v_show_progress
    """
    params: dict[str, object] = {}
    where_parts: list[str] = []
    if show_id is not None:
        where_parts.append("show_id = :show_id")
        params["show_id"] = show_id
    if user_id is not None:
        where_parts.append("user_id = :user_id")
        params["user_id"] = user_id
    if where_parts:
        statement += " WHERE " + " AND ".join(where_parts)
    statement += " ORDER BY show_title ASC, user_id ASC"
    rows = session.execute(text(statement), params).mappings().all()
    return [dict(row) for row in rows]


def list_show_episodes(
    session: Session,
    *,
    show_id: UUID,
    user_id: UUID | None,
) -> list[dict]:
    base_select = """
        SELECT
            mi.media_item_id,
            mi.title,
            mi.season_number,
            mi.episode_number,
            COUNT(*) FILTER (WHERE we.completed = TRUE) AS watched_count,
    """
    from_clause = """
        FROM app.media_item AS mi
        LEFT JOIN app.watch_event AS we
          ON we.media_item_id = mi.media_item_id
        WHERE mi.type = 'episode'::public.media_type
          AND mi.show_id = :show_id
        GROUP BY mi.media_item_id, mi.title, mi.season_number, mi.episode_number
        ORDER BY mi.season_number ASC NULLS LAST, mi.episode_number ASC NULLS LAST, mi.title ASC
    """
    params: dict[str, object] = {"show_id": show_id}

    if user_id is None:
        statement = (
            base_select
            + "            NULL::boolean AS watched_by_user\n"
            + from_clause
        )
    else:
        statement = (
            base_select
            + "            BOOL_OR(we.user_id = :user_id AND we.completed = TRUE) AS watched_by_user\n"
            + from_clause
        )
        params["user_id"] = user_id

    rows = session.execute(text(statement), params).mappings().all()
    return [dict(row) for row in rows]
