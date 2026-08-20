from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.datetime_utils import ensure_timezone_aware, to_utc_z_string
from app.repositories import media_items as media_item_repository
from app.repositories import watch_events as watch_event_repository
from app.schemas.jellyfin_integration import (
    JellyfinReconcileIssue,
    JellyfinReconcileRead,
    JellyfinReconcileRequest,
)
from app.services.import_batches import ImportBatchService
from app.services.jellyfin import JellyfinClient, JellyfinClientError
from app.services.users import UserService
from app.services.watch_events import WatchEventConstraintError, WatchEventService


class JellyfinReconciliationService:
    SOURCE = "jellyfin_reconcile"
    PLAYBACK_SOURCE = "jellyfin"
    FIRST_RUN_LOOKBACK_DAYS = 90
    CURSOR_OVERLAP_MINUTES = 5
    MAX_RETURNED_ISSUES = 100

    @staticmethod
    def run(
        session: Session,
        *,
        payload: JellyfinReconcileRequest,
        client: JellyfinClient | None = None,
        now: datetime | None = None,
    ) -> JellyfinReconcileRead:
        run_started_at = (now or datetime.now(UTC)).astimezone(UTC)
        user = UserService.get_user_by_id(session, payload.klug_user_id)
        if user is None:
            raise ValueError(f"User '{payload.klug_user_id}' not found")
        if user.jellyfin_user_id is None:
            raise ValueError("Klug user is not mapped to a Jellyfin user")

        since = JellyfinReconciliationService._resolve_since(
            session,
            user_id=user.user_id,
            explicit_since=payload.since,
            now=run_started_at,
        )
        source_detail = str(user.user_id)
        jellyfin_client = client or JellyfinClient.from_settings()
        batch = None
        if not payload.dry_run:
            batch = ImportBatchService.start_import_batch(
                session,
                source=JellyfinReconciliationService.SOURCE,
                source_detail=source_detail,
                notes=payload.notes,
                parameters={
                    "jellyfin_user_id": str(user.jellyfin_user_id),
                    "since": to_utc_z_string(since),
                    "cursor_before": to_utc_z_string(since),
                    "dry_run": False,
                },
            )

        try:
            items = jellyfin_client.list_played_items(
                user_id=user.jellyfin_user_id,
                changed_since=since,
            )
        except JellyfinClientError:
            if batch is not None:
                ImportBatchService.finish_import_batch(
                    session,
                    import_batch_id=batch.import_batch_id,
                    status="failed",
                    watch_events_inserted=0,
                    media_items_inserted=0,
                    media_versions_inserted=0,
                    tags_added=0,
                    errors_count=1,
                    notes=payload.notes,
                    parameters_patch={
                        "cursor_after": None,
                        "failure": "Jellyfin request failed",
                    },
                )
            raise

        scanned_count = len(items)
        candidate_count = 0
        inserted_count = 0
        already_present_count = 0
        unmatched_media_count = 0
        missing_timestamp_count = 0
        ambiguous_play_count = 0
        error_count = 0
        issues: list[JellyfinReconcileIssue] = []

        for item in items:
            if not item.played:
                continue
            if item.last_played_at is None:
                missing_timestamp_count += 1
                JellyfinReconciliationService._append_issue(
                    issues,
                    item_id=item.source_item_id,
                    title=item.title,
                    reason="missing_last_played_at",
                    play_count=item.play_count,
                    last_played_at=None,
                )
                continue
            if item.last_played_at < since:
                continue
            candidate_count += 1

            media_item = media_item_repository.find_media_item_by_jellyfin_item_id(
                session,
                jellyfin_item_id=item.source_item_id,
            )
            if media_item is None:
                unmatched_media_count += 1
                JellyfinReconciliationService._append_issue(
                    issues,
                    item_id=item.source_item_id,
                    title=item.title,
                    reason="unmatched_media",
                    play_count=item.play_count,
                    last_played_at=item.last_played_at,
                )
                continue

            collision_window_seconds = (
                get_settings().klug_watch_collision_window_seconds
            )
            existing = watch_event_repository.find_matching_watch_event(
                session,
                user_id=user.user_id,
                media_item_id=media_item.media_item_id,
                watched_at=item.last_played_at,
                completed=True,
                collision_window_seconds=collision_window_seconds,
                collision_window_after_seconds=(
                    collision_window_seconds + max(0, item.runtime_seconds or 0)
                ),
            )
            if existing is not None:
                already_present_count += 1
                continue

            if item.play_count > 1:
                ambiguous_play_count += 1
                JellyfinReconciliationService._append_issue(
                    issues,
                    item_id=item.source_item_id,
                    title=item.title,
                    reason="older_rewatch_dates_unavailable",
                    play_count=item.play_count,
                    last_played_at=item.last_played_at,
                )

            if payload.dry_run:
                inserted_count += 1
                continue

            try:
                result = WatchEventService.create_watch_event(
                    session,
                    user_id=user.user_id,
                    media_item_id=media_item.media_item_id,
                    watched_at=item.last_played_at,
                    playback_source=JellyfinReconciliationService.PLAYBACK_SOURCE,
                    total_seconds=item.runtime_seconds,
                    watched_seconds=None,
                    progress_percent=None,
                    completed=True,
                    rating_value=None,
                    rating_scale=None,
                    media_version_id=None,
                    source_event_id=(
                        JellyfinReconciliationService._source_event_id(
                            jellyfin_user_id=user.jellyfin_user_id,
                            item_id=item.source_item_id,
                            watched_at=item.last_played_at,
                        )
                    ),
                    import_batch_id=batch.import_batch_id,
                    origin_kind="manual_import",
                )
                if result.created:
                    inserted_count += 1
                else:
                    already_present_count += 1
            except (WatchEventConstraintError, ValueError) as exc:
                error_count += 1
                JellyfinReconciliationService._append_issue(
                    issues,
                    item_id=item.source_item_id,
                    title=item.title,
                    reason="watch_creation_failed",
                    play_count=item.play_count,
                    last_played_at=item.last_played_at,
                )
                ImportBatchService.add_import_batch_error(
                    session,
                    import_batch_id=batch.import_batch_id,
                    severity="error",
                    entity_type="jellyfin_item",
                    entity_ref=item.source_item_id,
                    message=str(exc),
                    details={"title": item.title},
                )

        status = (
            "dry_run"
            if payload.dry_run
            else ("completed_with_errors" if error_count else "completed")
        )
        import_batch_id = UUID("00000000-0000-0000-0000-000000000000")
        if batch is not None:
            finalized = ImportBatchService.finish_import_batch(
                session,
                import_batch_id=batch.import_batch_id,
                status=status,
                watch_events_inserted=inserted_count,
                media_items_inserted=0,
                media_versions_inserted=0,
                tags_added=0,
                errors_count=error_count,
                notes=payload.notes,
                parameters_patch={
                    "cursor_after": to_utc_z_string(run_started_at),
                    "scanned_count": scanned_count,
                    "candidate_count": candidate_count,
                    "already_present_count": already_present_count,
                    "unmatched_media_count": unmatched_media_count,
                    "missing_timestamp_count": missing_timestamp_count,
                    "ambiguous_play_count": ambiguous_play_count,
                    "issue_count": (
                        unmatched_media_count
                        + missing_timestamp_count
                        + ambiguous_play_count
                        + error_count
                    ),
                },
            )
            import_batch_id = finalized.import_batch_id

        issue_count = (
            unmatched_media_count
            + missing_timestamp_count
            + ambiguous_play_count
            + error_count
        )
        return JellyfinReconcileRead(
            import_batch_id=import_batch_id,
            status=status,
            dry_run=payload.dry_run,
            since=since,
            cursor_after=run_started_at,
            scanned_count=scanned_count,
            candidate_count=candidate_count,
            inserted_count=inserted_count,
            already_present_count=already_present_count,
            unmatched_media_count=unmatched_media_count,
            missing_timestamp_count=missing_timestamp_count,
            ambiguous_play_count=ambiguous_play_count,
            error_count=error_count,
            issue_count=issue_count,
            issues=issues,
        )

    @staticmethod
    def _resolve_since(
        session: Session,
        *,
        user_id: UUID,
        explicit_since: datetime | None,
        now: datetime,
    ) -> datetime:
        if explicit_since is not None:
            return ensure_timezone_aware(
                explicit_since,
                field_name="since",
            ).astimezone(UTC)

        latest = ImportBatchService.get_latest_completed_import_batch_for_source(
            session,
            source=JellyfinReconciliationService.SOURCE,
            source_detail=str(user_id),
        )
        if latest is not None:
            raw_cursor = (latest.parameters or {}).get("cursor_after")
            if isinstance(raw_cursor, str):
                try:
                    cursor = datetime.fromisoformat(raw_cursor.replace("Z", "+00:00"))
                    return ensure_timezone_aware(
                        cursor,
                        field_name="cursor_after",
                    ).astimezone(UTC) - timedelta(
                        minutes=JellyfinReconciliationService.CURSOR_OVERLAP_MINUTES
                    )
                except ValueError:
                    pass

        return now - timedelta(
            days=JellyfinReconciliationService.FIRST_RUN_LOOKBACK_DAYS
        )

    @staticmethod
    def _source_event_id(
        *, jellyfin_user_id: UUID, item_id: str, watched_at: datetime
    ) -> str:
        return (
            f"reconcile:{jellyfin_user_id.hex}:{item_id}:{to_utc_z_string(watched_at)}"
        )

    @staticmethod
    def _append_issue(
        issues: list[JellyfinReconcileIssue],
        *,
        item_id: str,
        title: str,
        reason: str,
        play_count: int,
        last_played_at: datetime | None,
    ) -> None:
        if len(issues) >= JellyfinReconciliationService.MAX_RETURNED_ISSUES:
            return
        issues.append(
            JellyfinReconcileIssue(
                item_id=item_id,
                title=title,
                reason=reason,
                play_count=play_count,
                last_played_at=last_played_at,
            )
        )
