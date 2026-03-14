from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.datetime_utils import ensure_timezone_aware
from app.db.models.entities import PlaybackEvent
from app.repositories import playback_events as playback_event_repository


class PlaybackEventConstraintError(Exception):
    """Raised when playback event persistence fails constraints."""


class PlaybackEventDuplicateError(PlaybackEventConstraintError):
    """Raised when the same playback event is recorded more than once."""


class PlaybackEventService:
    @staticmethod
    def record_playback_event(
        session: Session,
        *,
        collector: str,
        playback_source: str,
        event_type: str,
        user_id: UUID,
        occurred_at: datetime,
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
        progress_percent: Decimal | None,
        payload: dict,
    ) -> PlaybackEvent:
        normalized_collector = collector.strip()
        normalized_playback_source = playback_source.strip()
        normalized_event_type = event_type.strip()
        normalized_title = title.strip()
        normalized_source_event_id = source_event_id.strip() if source_event_id else None
        normalized_session_key = session_key.strip() if session_key else None
        normalized_imdb_id = imdb_id.strip() if imdb_id else None
        normalized_occurred_at = ensure_timezone_aware(
            occurred_at,
            field_name="occurred_at",
        )

        if not normalized_collector:
            raise ValueError("collector must not be empty")
        if not normalized_playback_source:
            raise ValueError("playback_source must not be empty")
        if not normalized_event_type:
            raise ValueError("event_type must not be empty")
        if not normalized_title:
            raise ValueError("title must not be empty")

        try:
            playback_event = playback_event_repository.create_playback_event(
                session,
                collector=normalized_collector,
                playback_source=normalized_playback_source,
                event_type=normalized_event_type,
                user_id=user_id,
                occurred_at=normalized_occurred_at,
                source_event_id=normalized_source_event_id,
                session_key=normalized_session_key,
                media_type=media_type,
                title=normalized_title,
                year=year,
                season_number=season_number,
                episode_number=episode_number,
                tmdb_id=tmdb_id,
                imdb_id=normalized_imdb_id,
                tvdb_id=tvdb_id,
                progress_percent=progress_percent,
                payload=payload,
            )
            session.commit()
            return playback_event
        except IntegrityError as exc:
            session.rollback()
            constraint_name = getattr(
                getattr(exc.orig, "diag", None), "constraint_name", None
            )
            if constraint_name == "ux_playback_event_source_event":
                raise PlaybackEventDuplicateError("Playback event already exists") from exc
            raise PlaybackEventConstraintError("Failed to record playback event") from exc
