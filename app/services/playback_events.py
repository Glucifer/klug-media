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
    def list_playback_events(
        session: Session,
        *,
        user_id: UUID | None,
        playback_source: str | None,
        collector: str | None,
        session_key: str | None,
        event_type: str | None,
        media_type: str | None,
        limit: int,
        offset: int,
    ) -> list[PlaybackEvent]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        normalized_playback_source = (
            playback_source.strip() if playback_source is not None else None
        )
        normalized_collector = collector.strip() if collector is not None else None
        normalized_session_key = session_key.strip() if session_key is not None else None
        normalized_event_type = event_type.strip() if event_type is not None else None
        normalized_media_type = media_type.strip() if media_type is not None else None

        return playback_event_repository.list_playback_events(
            session,
            user_id=user_id,
            playback_source=normalized_playback_source,
            collector=normalized_collector,
            session_key=normalized_session_key,
            event_type=normalized_event_type,
            media_type=normalized_media_type,
            limit=safe_limit,
            offset=safe_offset,
        )

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
        total_seconds: int | None,
        watched_seconds: int | None,
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
                total_seconds=total_seconds,
                watched_seconds=watched_seconds,
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

    @staticmethod
    def update_playback_event_decision(
        session: Session,
        *,
        playback_event: PlaybackEvent,
        decision_status: str,
        decision_reason: str | None,
        watch_id: UUID | None,
    ) -> PlaybackEvent:
        normalized_decision_status = decision_status.strip()
        normalized_decision_reason = (
            decision_reason.strip() if decision_reason is not None else None
        )
        if not normalized_decision_status:
            raise ValueError("decision_status must not be empty")

        try:
            updated = playback_event_repository.update_playback_event_decision(
                session,
                playback_event=playback_event,
                decision_status=normalized_decision_status,
                decision_reason=normalized_decision_reason,
                watch_id=watch_id,
            )
            session.commit()
            return updated
        except IntegrityError as exc:
            session.rollback()
            raise PlaybackEventConstraintError(
                "Failed to update playback event decision"
            ) from exc

    @staticmethod
    def session_has_prior_scrobble_candidate(
        session: Session,
        *,
        collector: str,
        playback_source: str,
        user_id: UUID,
        session_key: str,
        exclude_playback_event_id: UUID,
    ) -> bool:
        normalized_collector = collector.strip()
        normalized_playback_source = playback_source.strip()
        normalized_session_key = session_key.strip()

        if not normalized_collector:
            raise ValueError("collector must not be empty")
        if not normalized_playback_source:
            raise ValueError("playback_source must not be empty")
        if not normalized_session_key:
            raise ValueError("session_key must not be empty")

        return playback_event_repository.session_has_prior_scrobble_candidate(
            session,
            collector=normalized_collector,
            playback_source=normalized_playback_source,
            user_id=user_id,
            session_key=normalized_session_key,
            exclude_playback_event_id=exclude_playback_event_id,
        )

    @staticmethod
    def get_session_max_progress_percent(
        session: Session,
        *,
        collector: str,
        playback_source: str,
        user_id: UUID,
        session_key: str,
    ) -> float | None:
        normalized_collector = collector.strip()
        normalized_playback_source = playback_source.strip()
        normalized_session_key = session_key.strip()

        if not normalized_collector:
            raise ValueError("collector must not be empty")
        if not normalized_playback_source:
            raise ValueError("playback_source must not be empty")
        if not normalized_session_key:
            raise ValueError("session_key must not be empty")

        return playback_event_repository.get_session_max_progress_percent(
            session,
            collector=normalized_collector,
            playback_source=normalized_playback_source,
            user_id=user_id,
            session_key=normalized_session_key,
        )
