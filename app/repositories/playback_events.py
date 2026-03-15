from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.db.models.entities import PlaybackEvent


def list_playback_events(
    session: Session,
    *,
    user_id: UUID | None,
    playback_source: str | None,
    collector: str | None,
    session_key: str | None,
    event_type: str | None,
    media_type: str | None,
    decision_status: str | None,
    limit: int,
    offset: int,
) -> list[PlaybackEvent]:
    statement: Select[tuple[PlaybackEvent]] = select(PlaybackEvent)
    if user_id is not None:
        statement = statement.where(PlaybackEvent.user_id == user_id)
    if playback_source is not None:
        statement = statement.where(PlaybackEvent.playback_source == playback_source)
    if collector is not None:
        statement = statement.where(PlaybackEvent.collector == collector)
    if session_key is not None:
        statement = statement.where(PlaybackEvent.session_key == session_key)
    if event_type is not None:
        statement = statement.where(PlaybackEvent.event_type == event_type)
    if media_type is not None:
        statement = statement.where(PlaybackEvent.media_type == media_type)
    if decision_status is not None:
        statement = statement.where(PlaybackEvent.decision_status == decision_status)

    statement = (
        statement.order_by(PlaybackEvent.occurred_at.desc(), PlaybackEvent.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.scalars(statement))


def get_playback_event(
    session: Session,
    *,
    playback_event_id: UUID,
) -> PlaybackEvent | None:
    statement = select(PlaybackEvent).where(
        PlaybackEvent.playback_event_id == playback_event_id
    )
    return session.scalar(statement)


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
    total_seconds: int | None,
    watched_seconds: int | None,
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
        total_seconds=total_seconds,
        watched_seconds=watched_seconds,
        progress_percent=progress_percent,
        payload=payload,
    )
    session.add(playback_event)
    session.flush()
    session.refresh(playback_event)
    return playback_event


def update_playback_event_decision(
    session: Session,
    *,
    playback_event: PlaybackEvent,
    decision_status: str,
    decision_reason: str | None,
    watch_id: UUID | None,
) -> PlaybackEvent:
    playback_event.decision_status = decision_status
    playback_event.decision_reason = decision_reason
    playback_event.watch_id = watch_id
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


def session_has_prior_scrobble_candidate(
    session: Session,
    *,
    collector: str,
    playback_source: str,
    user_id: UUID,
    session_key: str,
    exclude_playback_event_id: UUID,
) -> bool:
    statement = select(PlaybackEvent.playback_event_id).where(
        PlaybackEvent.collector == collector,
        PlaybackEvent.playback_source == playback_source,
        PlaybackEvent.user_id == user_id,
        PlaybackEvent.session_key == session_key,
        PlaybackEvent.playback_event_id != exclude_playback_event_id,
        or_(
            PlaybackEvent.event_type == "scrobble",
            (
                (PlaybackEvent.event_type == "stop")
                & (PlaybackEvent.progress_percent.is_not(None))
                & (PlaybackEvent.progress_percent >= 90)
            ),
        ),
    )
    return session.scalar(statement) is not None


def get_session_max_progress_percent(
    session: Session,
    *,
    collector: str,
    playback_source: str,
    user_id: UUID,
    session_key: str,
) -> float | None:
    statement = select(func.max(PlaybackEvent.progress_percent)).where(
        PlaybackEvent.collector == collector,
        PlaybackEvent.playback_source == playback_source,
        PlaybackEvent.user_id == user_id,
        PlaybackEvent.session_key == session_key,
        PlaybackEvent.progress_percent.is_not(None),
    )
    max_progress = session.scalar(statement)
    if max_progress is None:
        return None
    return float(max_progress)
