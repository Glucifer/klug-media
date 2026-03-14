from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import PlaybackEvent


def create_playback_event(
    session: Session,
    *,
    collector: str,
    playback_source: str,
    event_type: str,
    user_id: UUID,
    occurred_at,
    source_event_id: str | None,
    session_key: str | None,
    media_type: str,
    title: str,
    year: int | None,
    season_number: int | None,
    episode_number: int | None,
    tmdb_id: int | None,
    imdb_id: str | None,
    tvdb_id: int | None,
    progress_percent,
    payload: dict,
) -> PlaybackEvent:
    playback_event = PlaybackEvent(
        collector=collector,
        playback_source=playback_source,
        event_type=event_type,
        user_id=user_id,
        occurred_at=occurred_at,
        source_event_id=source_event_id,
        session_key=session_key,
        media_type=media_type,
        title=title,
        year=year,
        season_number=season_number,
        episode_number=episode_number,
        tmdb_id=tmdb_id,
        imdb_id=imdb_id,
        tvdb_id=tvdb_id,
        progress_percent=progress_percent,
        payload=payload,
    )
    session.add(playback_event)
    session.flush()
    session.refresh(playback_event)
    return playback_event


def get_playback_event_by_source_event_id(
    session: Session,
    *,
    collector: str,
    source_event_id: str,
) -> PlaybackEvent | None:
    statement = select(PlaybackEvent).where(
        PlaybackEvent.collector == collector,
        PlaybackEvent.source_event_id == source_event_id,
    )
    return session.scalar(statement)
