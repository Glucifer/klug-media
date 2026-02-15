from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.imports import WatchEventImportRequest
from app.services.import_adapters import get_watch_event_import_adapter
from app.services.import_batches import ImportBatchService
from app.services.watch_events import WatchEventConstraintError, WatchEventService


@dataclass(frozen=True)
class WatchEventImportResult:
    import_batch_id: UUID
    status: str
    processed_count: int
    inserted_count: int
    error_count: int


class WatchEventImportService:
    @staticmethod
    def run_import(
        session: Session,
        *,
        payload: WatchEventImportRequest,
    ) -> WatchEventImportResult:
        adapter = get_watch_event_import_adapter(payload.source)

        source_detail = payload.source_detail or payload.mode.value
        batch = ImportBatchService.start_import_batch(
            session,
            source=payload.source,
            source_detail=source_detail,
            notes=payload.notes,
        )

        inserted_count = 0
        error_count = 0

        for index, event in enumerate(payload.events):
            mapped = adapter.to_watch_event_create_args(event)
            try:
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
        )

        return WatchEventImportResult(
            import_batch_id=finalized_batch.import_batch_id,
            status=finalized_batch.status,
            processed_count=len(payload.events),
            inserted_count=inserted_count,
            error_count=error_count,
        )
