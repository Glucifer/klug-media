from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.imports import (
    LegacySourceWatchEventImportRequest,
    WatchEventImportRequest,
)
from app.services.import_adapters import (
    LegacySourceWatchEventImportAdapter,
    get_watch_event_import_adapter,
)
from app.services.import_batches import ImportBatchService
from app.services.watch_events import (
    WatchEventConstraintError,
    WatchEventDuplicateError,
    WatchEventService,
)


@dataclass(frozen=True)
class WatchEventImportResult:
    import_batch_id: UUID
    status: str
    dry_run: bool
    processed_count: int
    inserted_count: int
    skipped_count: int
    error_count: int
    rejected_before_import: int = 0
    cursor_before: dict | None = None
    cursor_after: dict | None = None


class WatchEventImportService:
    @staticmethod
    def _to_cursor(
        *,
        watched_at: datetime,
        source_event_id: str | None,
    ) -> dict:
        return {
            "watched_at": watched_at.isoformat(),
            "source_event_id": source_event_id,
        }

    @staticmethod
    def _parse_cursor(cursor: dict | None) -> tuple[datetime, str] | None:
        if not cursor:
            return None
        watched_at_value = cursor.get("watched_at")
        if not isinstance(watched_at_value, str):
            return None

        normalized = watched_at_value.replace("Z", "+00:00")
        parsed_watched_at = datetime.fromisoformat(normalized)
        source_event_id = cursor.get("source_event_id") or ""
        return parsed_watched_at, source_event_id

    @staticmethod
    def _is_at_or_before_cursor(
        *,
        watched_at: datetime,
        source_event_id: str | None,
        cursor: dict | None,
    ) -> bool:
        parsed_cursor = WatchEventImportService._parse_cursor(cursor)
        if parsed_cursor is None:
            return False

        cursor_watched_at, cursor_source_event_id = parsed_cursor
        if watched_at < cursor_watched_at:
            return True
        if watched_at > cursor_watched_at:
            return False
        return (source_event_id or "") <= cursor_source_event_id

    @staticmethod
    def _resolve_cursor_before(
        session: Session,
        *,
        source: str,
        source_detail: str,
        resume_from_latest: bool,
    ) -> dict | None:
        if not resume_from_latest:
            return None

        latest_batch = ImportBatchService.get_latest_import_batch_for_source(
            session,
            source=source,
            source_detail=source_detail,
        )
        if latest_batch is None:
            return None

        parameters = latest_batch.parameters or {}
        cursor = parameters.get("cursor")
        if isinstance(cursor, dict):
            return cursor
        return None

    @staticmethod
    def _max_cursor(left: dict | None, right: dict | None) -> dict | None:
        if left is None:
            return right
        if right is None:
            return left

        left_key = WatchEventImportService._parse_cursor(left)
        right_key = WatchEventImportService._parse_cursor(right)
        if left_key is None:
            return right
        if right_key is None:
            return left
        return left if left_key >= right_key else right

    @staticmethod
    def run_import(
        session: Session,
        *,
        payload: WatchEventImportRequest,
    ) -> WatchEventImportResult:
        adapter = get_watch_event_import_adapter(payload.source)
        source_detail = payload.source_detail or payload.mode.value
        cursor_before = (
            WatchEventImportService._resolve_cursor_before(
                session,
                source=payload.source,
                source_detail=source_detail,
                resume_from_latest=payload.resume_from_latest,
            )
            if payload.mode.value == "incremental"
            else None
        )
        cursor_after = cursor_before

        inserted_count = 0
        skipped_count = 0
        error_count = 0

        if payload.dry_run:
            for event in payload.events:
                mapped = adapter.to_watch_event_create_args(event)
                if not mapped.playback_source.strip():
                    error_count += 1
                else:
                    if payload.mode.value == "incremental" and (
                        WatchEventImportService._is_at_or_before_cursor(
                            watched_at=mapped.watched_at,
                            source_event_id=mapped.source_event_id,
                            cursor=cursor_before,
                        )
                    ):
                        skipped_count += 1
                        continue
                    cursor_after = WatchEventImportService._max_cursor(
                        cursor_after,
                        WatchEventImportService._to_cursor(
                            watched_at=mapped.watched_at,
                            source_event_id=mapped.source_event_id,
                        ),
                    )
                    inserted_count += 1
            return WatchEventImportResult(
                import_batch_id=UUID("00000000-0000-0000-0000-000000000000"),
                status="dry_run",
                dry_run=True,
                processed_count=len(payload.events),
                inserted_count=inserted_count,
                skipped_count=skipped_count,
                error_count=error_count,
                rejected_before_import=payload.rejected_before_import,
                cursor_before=cursor_before,
                cursor_after=cursor_after,
            )

        batch = ImportBatchService.start_import_batch(
            session,
            source=payload.source,
            source_detail=source_detail,
            notes=payload.notes,
            parameters={
                "mode": payload.mode.value,
                "resume_from_latest": payload.resume_from_latest,
                "cursor_before": cursor_before,
                "rejected_before_import": payload.rejected_before_import,
            },
        )

        for index, event in enumerate(payload.events):
            mapped = adapter.to_watch_event_create_args(event)
            row_cursor = WatchEventImportService._to_cursor(
                watched_at=mapped.watched_at,
                source_event_id=mapped.source_event_id,
            )

            if payload.mode.value == "incremental" and (
                WatchEventImportService._is_at_or_before_cursor(
                    watched_at=mapped.watched_at,
                    source_event_id=mapped.source_event_id,
                    cursor=cursor_before,
                )
            ):
                skipped_count += 1
                continue

            try:
                if payload.mode.value == "incremental" and mapped.source_event_id:
                    if WatchEventService.source_event_exists(
                        session,
                        playback_source=mapped.playback_source,
                        source_event_id=mapped.source_event_id,
                    ):
                        skipped_count += 1
                        cursor_after = WatchEventImportService._max_cursor(
                            cursor_after, row_cursor
                        )
                        continue

                WatchEventService.create_watch_event(
                    session,
                    user_id=mapped.user_id,
                    media_item_id=mapped.media_item_id,
                    watched_at=mapped.watched_at,
                    playback_source=mapped.playback_source,
                    total_seconds=mapped.total_seconds,
                    watched_seconds=mapped.watched_seconds,
                    progress_percent=mapped.progress_percent,
                    completed=mapped.completed,
                    rating_value=mapped.rating_value,
                    rating_scale=mapped.rating_scale,
                    media_version_id=mapped.media_version_id,
                    source_event_id=mapped.source_event_id,
                )
                inserted_count += 1
                cursor_after = WatchEventImportService._max_cursor(
                    cursor_after, row_cursor
                )
            except WatchEventDuplicateError:
                skipped_count += 1
                cursor_after = WatchEventImportService._max_cursor(
                    cursor_after, row_cursor
                )
            except (WatchEventConstraintError, ValueError) as exc:
                error_count += 1
                ImportBatchService.add_import_batch_error(
                    session,
                    import_batch_id=batch.import_batch_id,
                    severity="error",
                    entity_type="watch_event",
                    entity_ref=mapped.source_event_id or str(index),
                    message=str(exc),
                    details={"row_index": index, "mode": payload.mode.value},
                )

        final_status = "completed" if error_count == 0 else "completed_with_errors"
        finalized_batch = ImportBatchService.finish_import_batch(
            session,
            import_batch_id=batch.import_batch_id,
            status=final_status,
            watch_events_inserted=inserted_count,
            media_items_inserted=0,
            media_versions_inserted=0,
            tags_added=0,
            errors_count=error_count,
            notes=payload.notes,
            parameters_patch={
                "cursor_before": cursor_before,
                "cursor": cursor_after,
                "rejected_before_import": payload.rejected_before_import,
            },
        )

        return WatchEventImportResult(
            import_batch_id=finalized_batch.import_batch_id,
            status=finalized_batch.status,
            dry_run=False,
            processed_count=len(payload.events),
            inserted_count=inserted_count,
            skipped_count=skipped_count,
            error_count=error_count,
            rejected_before_import=payload.rejected_before_import,
            cursor_before=cursor_before,
            cursor_after=cursor_after,
        )

    @staticmethod
    def run_legacy_source_import(
        session: Session,
        *,
        payload: LegacySourceWatchEventImportRequest,
    ) -> WatchEventImportResult:
        adapter = LegacySourceWatchEventImportAdapter()
        internal_events = [adapter.to_internal_event(row) for row in payload.rows]
        internal_payload = WatchEventImportRequest(
            source="legacy_source_export",
            mode=payload.mode,
            dry_run=payload.dry_run,
            resume_from_latest=payload.resume_from_latest,
            source_detail=payload.source_detail,
            notes=payload.notes,
            rejected_before_import=payload.rejected_before_import,
            events=internal_events,
        )
        return WatchEventImportService.run_import(session, payload=internal_payload)
