from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.datetime_utils import ensure_timezone_aware
from app.db.models.entities import WatchEvent
from app.repositories import watch_events as watch_event_repository


class WatchEventConstraintError(Exception):
    """Raised when a watch event violates database constraints."""


class WatchEventDuplicateError(WatchEventConstraintError):
    """Raised when a watch event is a duplicate."""


@dataclass(frozen=True)
class WatchEventCreateResult:
    watch_event: WatchEvent
    created: bool
    matched_existing: bool = False
    match_reason: str | None = None


class WatchEventService:
    VALID_ORIGIN_KINDS = {"live_playback", "manual_import", "manual_entry"}

    @staticmethod
    def list_watch_events(
        session: Session,
        *,
        user_id: UUID | None,
        media_item_id: UUID | None,
        watched_after: datetime | None,
        watched_before: datetime | None,
        local_date_from: date | None,
        local_date_to: date | None,
        media_type: Literal["movie", "show", "episode"] | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, object]]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        return watch_event_repository.list_watch_events(
            session,
            user_id=user_id,
            media_item_id=media_item_id,
            watched_after=watched_after,
            watched_before=watched_before,
            local_date_from=local_date_from,
            local_date_to=local_date_to,
            media_type=media_type,
            limit=safe_limit,
            offset=safe_offset,
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
        created_by: str | None = None,
        import_batch_id: UUID | None = None,
        origin_kind: str = "manual_entry",
        origin_playback_event_id: UUID | None = None,
    ) -> WatchEventCreateResult:
        normalized_playback_source = playback_source.strip()
        if not normalized_playback_source:
            raise ValueError("playback_source must not be empty")
        normalized_watched_at = ensure_timezone_aware(
            watched_at,
            field_name="watched_at",
        ).astimezone(UTC)

        normalized_rating_scale = rating_scale.strip() if rating_scale else None
        normalized_source_event_id = source_event_id.strip() if source_event_id else None
        normalized_created_by = created_by.strip() if created_by else None
        normalized_origin_kind = origin_kind.strip()
        if not normalized_origin_kind:
            raise ValueError("origin_kind must not be empty")
        if normalized_origin_kind not in WatchEventService.VALID_ORIGIN_KINDS:
            raise ValueError("origin_kind must be a supported provenance value")

        if normalized_source_event_id:
            existing_by_source = watch_event_repository.get_watch_event_by_source_event(
                session,
                playback_source=normalized_playback_source,
                source_event_id=normalized_source_event_id,
            )
            if existing_by_source is not None:
                return WatchEventCreateResult(
                    watch_event=existing_by_source,
                    created=False,
                    matched_existing=True,
                    match_reason="source_event",
                )

        collision_match = watch_event_repository.find_matching_watch_event(
            session,
            user_id=user_id,
            media_item_id=media_item_id,
            watched_at=normalized_watched_at,
            completed=completed,
            collision_window_seconds=WatchEventService._watch_collision_window_seconds(),
        )
        if collision_match is not None:
            return WatchEventCreateResult(
                watch_event=collision_match,
                created=False,
                matched_existing=True,
                match_reason="collision_window",
            )

        is_rewatch = watch_event_repository.prior_watch_event_exists(
            session,
            user_id=user_id,
            media_item_id=media_item_id,
            watched_at=normalized_watched_at,
        )

        try:
            watch_event = watch_event_repository.create_watch_event(
                session,
                user_id=user_id,
                media_item_id=media_item_id,
                watched_at=normalized_watched_at,
                playback_source=normalized_playback_source,
                total_seconds=total_seconds,
                watched_seconds=watched_seconds,
                progress_percent=progress_percent,
                completed=completed,
                rating_value=rating_value,
                rating_scale=normalized_rating_scale,
                media_version_id=media_version_id,
                source_event_id=normalized_source_event_id,
                created_by=normalized_created_by,
                import_batch_id=import_batch_id,
                origin_kind=normalized_origin_kind,
                origin_playback_event_id=origin_playback_event_id,
                rewatch=is_rewatch,
            )
            session.commit()
            return WatchEventCreateResult(
                watch_event=watch_event,
                created=True,
            )
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

    @staticmethod
    def _watch_collision_window_seconds() -> int:
        return max(0, get_settings().klug_watch_collision_window_seconds)
