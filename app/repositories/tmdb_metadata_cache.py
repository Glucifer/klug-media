from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import TmdbMetadataCache


def get_cache_entry(
    session: Session,
    *,
    tmdb_type: str,
    tmdb_id: int,
    sub_key: str,
) -> TmdbMetadataCache | None:
    statement = select(TmdbMetadataCache).where(
        TmdbMetadataCache.tmdb_type == tmdb_type,
        TmdbMetadataCache.tmdb_id == tmdb_id,
        TmdbMetadataCache.sub_key == sub_key,
    )
    return session.scalar(statement)


def upsert_cache_entry(
    session: Session,
    *,
    tmdb_type: str,
    tmdb_id: int,
    sub_key: str,
    payload: dict,
    fetched_at: datetime,
    expires_at: datetime | None,
    etag: str | None,
    source_url: str | None,
) -> TmdbMetadataCache:
    existing = get_cache_entry(
        session,
        tmdb_type=tmdb_type,
        tmdb_id=tmdb_id,
        sub_key=sub_key,
    )
    if existing is None:
        existing = TmdbMetadataCache(
            tmdb_type=tmdb_type,
            tmdb_id=tmdb_id,
            sub_key=sub_key,
        )

    existing.payload = payload
    existing.fetched_at = fetched_at
    existing.expires_at = expires_at
    existing.etag = etag
    existing.source_url = source_url
    session.add(existing)
    session.flush()
    session.refresh(existing)
    return existing
