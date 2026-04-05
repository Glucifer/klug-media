from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, or_, select, update
from sqlalchemy.orm import Session

from app.db.models.entities import CollectionEntry, MediaItem, Show


def find_collection_entry_by_source_item(
    session: Session,
    *,
    source: str,
    source_item_id: str,
) -> CollectionEntry | None:
    statement = select(CollectionEntry).where(
        CollectionEntry.source == source,
        CollectionEntry.source_item_id == source_item_id,
    )
    return session.scalar(statement)


def create_collection_entry(
    session: Session,
    *,
    source: str,
    source_item_id: str,
    item_type: str,
    library_id: str,
    library_name: str | None,
    media_item_id: UUID | None,
    show_id: UUID | None,
    seen_at: datetime,
    added_at: datetime | None,
    runtime_seconds: int | None,
    file_path: str | None,
    source_data: dict,
) -> CollectionEntry:
    entry = CollectionEntry(
        source=source,
        source_item_id=source_item_id,
        item_type=item_type,
        library_id=library_id,
        library_name=library_name,
        media_item_id=media_item_id,
        show_id=show_id,
        is_present=True,
        first_seen_at=seen_at,
        last_seen_at=seen_at,
        missing_since=None,
        added_at=added_at,
        runtime_seconds=runtime_seconds,
        file_path=file_path,
        source_data=source_data,
        updated_at=seen_at,
    )
    session.add(entry)
    session.flush()
    session.refresh(entry)
    return entry


def update_collection_entry(
    session: Session,
    *,
    entry: CollectionEntry,
    media_item_id: UUID | None,
    show_id: UUID | None,
    library_id: str,
    library_name: str | None,
    seen_at: datetime,
    added_at: datetime | None,
    runtime_seconds: int | None,
    file_path: str | None,
    source_data: dict,
) -> CollectionEntry:
    entry.media_item_id = media_item_id
    entry.show_id = show_id
    entry.library_id = library_id
    entry.library_name = library_name
    entry.is_present = True
    entry.last_seen_at = seen_at
    entry.missing_since = None
    entry.added_at = added_at
    entry.runtime_seconds = runtime_seconds
    entry.file_path = file_path
    entry.source_data = source_data
    entry.updated_at = seen_at
    session.add(entry)
    session.flush()
    session.refresh(entry)
    return entry


def mark_missing_entries(
    session: Session,
    *,
    source: str,
    library_ids: list[str],
    seen_source_item_ids: set[str],
    missing_since: datetime,
) -> int:
    statement = update(CollectionEntry).where(
        CollectionEntry.source == source,
        CollectionEntry.library_id.in_(library_ids),
        CollectionEntry.is_present.is_(True),
    )
    if seen_source_item_ids:
        statement = statement.where(
            CollectionEntry.source_item_id.not_in(sorted(seen_source_item_ids))
        )
    values = {
        "is_present": False,
        "missing_since": missing_since,
        "updated_at": missing_since,
    }
    result = session.execute(statement.values(**values))
    return int(result.rowcount or 0)


def count_entries_to_mark_missing(
    session: Session,
    *,
    source: str,
    library_ids: list[str],
    seen_source_item_ids: set[str],
) -> int:
    statement = select(func.count(CollectionEntry.collection_entry_id)).where(
        CollectionEntry.source == source,
        CollectionEntry.library_id.in_(library_ids),
        CollectionEntry.is_present.is_(True),
    )
    if seen_source_item_ids:
        statement = statement.where(
            CollectionEntry.source_item_id.not_in(sorted(seen_source_item_ids))
        )
    return int(session.scalar(statement) or 0)


def _present_filter(statement: Select, *, present: bool | None) -> Select:
    if present is None:
        return statement
    return statement.where(CollectionEntry.is_present.is_(present))


def list_collection_movies(
    session: Session,
    *,
    query: str | None,
    present: bool | None,
    limit: int,
    offset: int,
) -> list[dict]:
    statement = (
        select(
            CollectionEntry.collection_entry_id,
            CollectionEntry.source,
            CollectionEntry.source_item_id,
            MediaItem.media_item_id,
            MediaItem.title,
            MediaItem.year,
            MediaItem.tmdb_id,
            MediaItem.imdb_id,
            MediaItem.tvdb_id,
            CollectionEntry.is_present,
            CollectionEntry.first_seen_at,
            CollectionEntry.last_seen_at,
            CollectionEntry.missing_since,
            CollectionEntry.library_id,
            CollectionEntry.library_name,
            CollectionEntry.added_at,
            CollectionEntry.runtime_seconds,
            CollectionEntry.file_path,
        )
        .join(MediaItem, MediaItem.media_item_id == CollectionEntry.media_item_id)
        .where(CollectionEntry.item_type == "movie")
    )
    if query:
        statement = statement.where(MediaItem.title.ilike(f"%{query}%"))
    statement = _present_filter(statement, present=present)
    statement = statement.order_by(
        desc(CollectionEntry.is_present),
        asc(MediaItem.title),
        asc(CollectionEntry.collection_entry_id),
    ).limit(limit).offset(offset)
    return [dict(row) for row in session.execute(statement).mappings().all()]


def list_collection_shows(
    session: Session,
    *,
    query: str | None,
    present: bool | None,
    limit: int,
    offset: int,
) -> list[dict]:
    statement = (
        select(
            CollectionEntry.collection_entry_id,
            CollectionEntry.source,
            CollectionEntry.source_item_id,
            Show.show_id,
            Show.title,
            Show.year,
            Show.tmdb_id,
            Show.imdb_id,
            Show.tvdb_id,
            CollectionEntry.is_present,
            CollectionEntry.first_seen_at,
            CollectionEntry.last_seen_at,
            CollectionEntry.missing_since,
            CollectionEntry.library_id,
            CollectionEntry.library_name,
            CollectionEntry.added_at,
            CollectionEntry.runtime_seconds,
            CollectionEntry.file_path,
        )
        .join(Show, Show.show_id == CollectionEntry.show_id)
        .where(CollectionEntry.item_type == "show")
    )
    if query:
        statement = statement.where(Show.title.ilike(f"%{query}%"))
    statement = _present_filter(statement, present=present)
    statement = statement.order_by(
        desc(CollectionEntry.is_present),
        asc(Show.title),
        asc(CollectionEntry.collection_entry_id),
    ).limit(limit).offset(offset)
    return [dict(row) for row in session.execute(statement).mappings().all()]


def list_collection_episodes(
    session: Session,
    *,
    query: str | None,
    present: bool | None,
    limit: int,
    offset: int,
) -> list[dict]:
    statement = (
        select(
            CollectionEntry.collection_entry_id,
            CollectionEntry.source,
            CollectionEntry.source_item_id,
            MediaItem.media_item_id,
            Show.show_id,
            Show.title.label("show_title"),
            MediaItem.title,
            MediaItem.season_number,
            MediaItem.episode_number,
            MediaItem.year,
            MediaItem.tmdb_id,
            MediaItem.imdb_id,
            MediaItem.tvdb_id,
            CollectionEntry.is_present,
            CollectionEntry.first_seen_at,
            CollectionEntry.last_seen_at,
            CollectionEntry.missing_since,
            CollectionEntry.library_id,
            CollectionEntry.library_name,
            CollectionEntry.added_at,
            CollectionEntry.runtime_seconds,
            CollectionEntry.file_path,
        )
        .join(MediaItem, MediaItem.media_item_id == CollectionEntry.media_item_id)
        .outerjoin(Show, Show.show_id == MediaItem.show_id)
        .where(CollectionEntry.item_type == "episode")
    )
    if query:
        pattern = f"%{query}%"
        statement = statement.where(
            or_(MediaItem.title.ilike(pattern), Show.title.ilike(pattern))
        )
    statement = _present_filter(statement, present=present)
    statement = statement.order_by(
        desc(CollectionEntry.is_present),
        asc(Show.title).nulls_last(),
        asc(MediaItem.season_number).nulls_last(),
        asc(MediaItem.episode_number).nulls_last(),
        asc(MediaItem.title),
    ).limit(limit).offset(offset)
    return [dict(row) for row in session.execute(statement).mappings().all()]
