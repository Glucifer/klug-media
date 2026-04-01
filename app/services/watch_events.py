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
from app.services.media_items import MediaItemService
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
        include_deleted: bool,
        deleted_only: bool,
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
            include_deleted=include_deleted,
            deleted_only=deleted_only,
            limit=safe_limit,
            offset=safe_offset,
        )

    @staticmethod
    def list_unrated_watch_events(
        session: Session,
        *,
        user_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, object]]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        return watch_event_repository.list_unrated_watch_events(
            session,
            user_id=user_id,
            limit=safe_limit,
            offset=safe_offset,
        )

    @staticmethod
    def soft_delete_watch_event(
        session: Session,
        *,
        watch_id: UUID,
        updated_by: str,
        update_reason: str | None,
    ) -> WatchEvent:
        watch_event = WatchEventService._get_watch_event_or_raise(session, watch_id=watch_id)
        normalized_updated_by = WatchEventService._normalize_updated_by(updated_by)
        normalized_reason = WatchEventService._normalize_update_reason(update_reason)
        now = datetime.now(UTC)

        if watch_event.is_deleted:
            raise ValueError("Watch event is already deleted")

        watch_event.is_deleted = True
        watch_event.deleted_at = now
        watch_event.deleted_by = normalized_updated_by
        watch_event.deleted_reason = normalized_reason
        watch_event.updated_at = now
        watch_event.updated_by = normalized_updated_by
        watch_event.update_reason = normalized_reason
        watch_event.rewatch = False
        watch_event.dedupe_hash = None
        try:
            updated = watch_event_repository.update_watch_event(session, watch_event=watch_event)
            WatchEventService._recompute_rewatch_for_media_timeline(
                session,
                user_id=updated.user_id,
                media_item_id=updated.media_item_id,
            )
            session.commit()
            return updated
        except IntegrityError as exc:
            session.rollback()
            raise WatchEventConstraintError("Watch event failed database constraints") from exc

    @staticmethod
    def restore_watch_event(
        session: Session,
        *,
        watch_id: UUID,
        updated_by: str,
        update_reason: str | None,
    ) -> WatchEvent:
        watch_event = WatchEventService._get_watch_event_or_raise(session, watch_id=watch_id)
        normalized_updated_by = WatchEventService._normalize_updated_by(updated_by)
        normalized_reason = WatchEventService._normalize_update_reason(update_reason)
        now = datetime.now(UTC)

        if not watch_event.is_deleted:
            raise ValueError("Watch event is not deleted")

        watch_event.is_deleted = False
        watch_event.deleted_at = None
        watch_event.deleted_by = None
        watch_event.deleted_reason = None
        watch_event.updated_at = now
        watch_event.updated_by = normalized_updated_by
        watch_event.update_reason = normalized_reason
        watch_event.dedupe_hash = None
        try:
            updated = watch_event_repository.update_watch_event(session, watch_event=watch_event)
            WatchEventService._recompute_rewatch_for_media_timeline(
                session,
                user_id=updated.user_id,
                media_item_id=updated.media_item_id,
            )
            session.commit()
            return updated
        except IntegrityError as exc:
            session.rollback()
            raise WatchEventConstraintError("Watch event failed database constraints") from exc

    @staticmethod
    def correct_watch_event(
        session: Session,
        *,
        watch_id: UUID,
        updated_by: str,
        update_reason: str | None,
        watched_at: datetime | None,
        media_item_id: UUID | None,
        completed: bool | None,
        rewatch: bool | None,
    ) -> WatchEvent:
        watch_event = WatchEventService._get_watch_event_or_raise(session, watch_id=watch_id)
        normalized_updated_by = WatchEventService._normalize_updated_by(updated_by)
        normalized_reason = WatchEventService._normalize_update_reason(update_reason)

        if (
            watched_at is None
            and media_item_id is None
            and completed is None
            and rewatch is None
        ):
            raise ValueError("At least one correction field must be provided")

        previous_media_item_id = watch_event.media_item_id
        new_watched_at = (
            ensure_timezone_aware(watched_at, field_name="watched_at").astimezone(UTC)
            if watched_at is not None
            else watch_event.watched_at
        )
        if media_item_id is not None:
            media_item = MediaItemService.get_media_item(session, media_item_id=media_item_id)
            if media_item is None:
                raise ValueError(f"Media item '{media_item_id}' not found")
            watch_event.media_item_id = media_item_id
            if (
                watch_event.media_version_id is not None
                and not watch_event_repository.media_version_matches_media_item(
                    session,
                    media_version_id=watch_event.media_version_id,
                    media_item_id=media_item_id,
                )
            ):
                watch_event.media_version_id = None

        watch_event.watched_at = new_watched_at
        if completed is not None:
            watch_event.completed = completed
        if rewatch is not None:
            watch_event.rewatch = rewatch

        now = datetime.now(UTC)
        watch_event.updated_at = now
        watch_event.updated_by = normalized_updated_by
        watch_event.update_reason = normalized_reason
        if (
            media_item_id is not None
            or watched_at is not None
            or completed is not None
        ):
            watch_event.dedupe_hash = None
        try:
            updated = watch_event_repository.update_watch_event(session, watch_event=watch_event)

            if media_item_id is not None or watched_at is not None:
                WatchEventService._recompute_rewatch_for_media_timeline(
                    session,
                    user_id=updated.user_id,
                    media_item_id=previous_media_item_id,
                )
                if updated.media_item_id != previous_media_item_id:
                    WatchEventService._recompute_rewatch_for_media_timeline(
                        session,
                        user_id=updated.user_id,
                        media_item_id=updated.media_item_id,
                    )
            elif rewatch is None:
                updated.rewatch = watch_event_repository.prior_watch_event_exists(
                    session,
                    user_id=updated.user_id,
                    media_item_id=updated.media_item_id,
                    watched_at=updated.watched_at,
                )
                updated = watch_event_repository.update_watch_event(session, watch_event=updated)

            session.commit()
            return updated
        except IntegrityError as exc:
            session.rollback()
            raise WatchEventConstraintError("Watch event failed database constraints") from exc

    @staticmethod
    def rate_watch_event(
        session: Session,
        *,
        watch_id: UUID,
        updated_by: str,
        update_reason: str | None,
        rating_value: int,
    ) -> WatchEvent:
        watch_event = WatchEventService._get_watch_event_or_raise(session, watch_id=watch_id)
        normalized_updated_by = WatchEventService._normalize_updated_by(updated_by)
        normalized_reason = WatchEventService._normalize_update_reason(update_reason)
        if watch_event.is_deleted:
            raise ValueError("Cannot rate a deleted watch event")
        if rating_value < 1 or rating_value > 10:
            raise ValueError("rating_value must be between 1 and 10")

        watch_event.rating_value = Decimal(rating_value)
        watch_event.rating_scale = "10-star"
        watch_event.updated_at = datetime.now(UTC)
        watch_event.updated_by = normalized_updated_by
        watch_event.update_reason = normalized_reason
        try:
            updated = watch_event_repository.update_watch_event(session, watch_event=watch_event)
            session.commit()
            return updated
        except IntegrityError as exc:
            session.rollback()
            raise WatchEventConstraintError("Watch event failed database constraints") from exc

    @staticmethod
    def set_watch_event_version_override(
        session: Session,
        *,
        watch_id: UUID,
        updated_by: str,
        update_reason: str | None,
        version_name: str | None,
        runtime_minutes: int | None,
        clear_override: bool,
    ) -> WatchEvent:
        watch_event = WatchEventService._get_watch_event_or_raise(session, watch_id=watch_id)
        normalized_updated_by = WatchEventService._normalize_updated_by(updated_by)
        normalized_reason = WatchEventService._normalize_update_reason(update_reason)
        if watch_event.is_deleted:
            raise ValueError("Cannot edit version for a deleted watch event")

        if clear_override:
            watch_event.watch_version_name = None
            watch_event.watch_runtime_seconds = None
        else:
            normalized_version_name = version_name.strip() if version_name else ""
            if not normalized_version_name:
                raise ValueError("version_name must not be empty unless clearing override")
            watch_event.watch_version_name = normalized_version_name
            watch_event.watch_runtime_seconds = (
                runtime_minutes * 60 if runtime_minutes is not None else None
            )

        watch_event.updated_at = datetime.now(UTC)
        watch_event.updated_by = normalized_updated_by
        watch_event.update_reason = normalized_reason
        watch_event.dedupe_hash = None
        try:
            updated = watch_event_repository.update_watch_event(session, watch_event=watch_event)
            session.commit()
            return updated
        except IntegrityError as exc:
            session.rollback()
            raise WatchEventConstraintError("Watch event failed database constraints") from exc

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

    @staticmethod
    def _get_watch_event_or_raise(session: Session, *, watch_id: UUID) -> WatchEvent:
        watch_event = watch_event_repository.get_watch_event(session, watch_id=watch_id)
        if watch_event is None:
            raise ValueError(f"Watch event '{watch_id}' not found")
        return watch_event

    @staticmethod
    def _normalize_updated_by(updated_by: str) -> str:
        normalized = updated_by.strip()
        if not normalized:
            raise ValueError("updated_by must not be empty")
        return normalized

    @staticmethod
    def _normalize_update_reason(update_reason: str | None) -> str | None:
        if update_reason is None:
            return None
        normalized = update_reason.strip()
        return normalized or None

    @staticmethod
    def _recompute_rewatch_for_media_timeline(
        session: Session,
        *,
        user_id: UUID,
        media_item_id: UUID,
    ) -> None:
        watch_events = watch_event_repository.list_user_media_watch_events(
            session,
            user_id=user_id,
            media_item_id=media_item_id,
        )
        seen_active_watch = False
        for watch_event in watch_events:
            desired_rewatch = False if watch_event.is_deleted else seen_active_watch
            if watch_event.rewatch != desired_rewatch:
                watch_event.rewatch = desired_rewatch
                session.add(watch_event)
            if not watch_event.is_deleted:
                seen_active_watch = True
