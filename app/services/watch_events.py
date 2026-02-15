from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.entities import WatchEvent
from app.repositories import watch_events as watch_event_repository


class WatchEventConstraintError(Exception):
    """Raised when a watch event violates database constraints."""


class WatchEventDuplicateError(WatchEventConstraintError):
    """Raised when a watch event is a duplicate."""


class WatchEventService:
    @staticmethod
    def list_watch_events(
        session: Session,
        *,
        user_id: UUID | None,
        media_item_id: UUID | None,
        watched_after: datetime | None,
        watched_before: datetime | None,
        limit: int,
    ) -> list[WatchEvent]:
        safe_limit = max(1, min(limit, 100))
        return watch_event_repository.list_watch_events(
            session,
            user_id=user_id,
            media_item_id=media_item_id,
            watched_after=watched_after,
            watched_before=watched_before,
            limit=safe_limit,
        )

    @staticmethod
    def create_watch_event(
        session: Session,
        *,
        user_id: UUID,
        media_item_id: UUID,
        watched_at: datetime,
        playback_source: str,
        total_seconds: int | None,
        watched_seconds: int | None,
        progress_percent: Decimal | None,
        completed: bool,
        rating_value: Decimal | None,
        rating_scale: str | None,
        media_version_id: UUID | None,
        source_event_id: str | None,
    ) -> WatchEvent:
        normalized_playback_source = playback_source.strip()
        if not normalized_playback_source:
            raise ValueError("playback_source must not be empty")

        normalized_rating_scale = rating_scale.strip() if rating_scale else None

        try:
            watch_event = watch_event_repository.create_watch_event(
                session,
                user_id=user_id,
                media_item_id=media_item_id,
                watched_at=watched_at,
                playback_source=normalized_playback_source,
                total_seconds=total_seconds,
                watched_seconds=watched_seconds,
                progress_percent=progress_percent,
                completed=completed,
                rating_value=rating_value,
                rating_scale=normalized_rating_scale,
                media_version_id=media_version_id,
                source_event_id=source_event_id,
            )
            session.commit()
            return watch_event
        except IntegrityError as exc:
            session.rollback()
            sqlstate = getattr(exc.orig, "sqlstate", None) or getattr(
                exc.orig, "pgcode", None
            )
            constraint_name = getattr(
                getattr(exc.orig, "diag", None), "constraint_name", None
            )
            if sqlstate == "23505" and constraint_name in {
                "ux_watch_event_dedupe_hash",
                "ux_watch_event_source_event",
            }:
                raise WatchEventDuplicateError("Watch event already exists") from exc

            raise WatchEventConstraintError(
                "Watch event failed database constraints"
            ) from exc

    @staticmethod
    def source_event_exists(
        session: Session,
        *,
        playback_source: str,
        source_event_id: str,
    ) -> bool:
        return watch_event_repository.source_event_exists(
            session,
            playback_source=playback_source,
            source_event_id=source_event_id,
        )
