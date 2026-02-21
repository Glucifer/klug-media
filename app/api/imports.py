from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.imports import (
    LegacySourceWatchEventImportRequest,
    WatchEventImportRequest,
    WatchEventImportResponse,
)
from app.services.imports import WatchEventImportService

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/watch-events", response_model=WatchEventImportResponse)
def import_watch_events(
    payload: WatchEventImportRequest,
    session: Session = Depends(get_db_session),
) -> WatchEventImportResponse:
    try:
        result = WatchEventImportService.run_import(session, payload=payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return WatchEventImportResponse(
        import_batch_id=result.import_batch_id,
        status=result.status,
        dry_run=result.dry_run,
        processed_count=result.processed_count,
        inserted_count=result.inserted_count,
        skipped_count=result.skipped_count,
        error_count=result.error_count,
        rejected_before_import=result.rejected_before_import,
        media_items_created=result.media_items_created,
        shows_created=result.shows_created,
        cursor_before=result.cursor_before,
        cursor_after=result.cursor_after,
    )


@router.post("/watch-events/legacy-source", response_model=WatchEventImportResponse)
def import_legacy_source_watch_events(
    payload: LegacySourceWatchEventImportRequest,
    session: Session = Depends(get_db_session),
) -> WatchEventImportResponse:
    result = WatchEventImportService.run_legacy_source_import(session, payload=payload)
    return WatchEventImportResponse(
        import_batch_id=result.import_batch_id,
        status=result.status,
        dry_run=result.dry_run,
        processed_count=result.processed_count,
        inserted_count=result.inserted_count,
        skipped_count=result.skipped_count,
        error_count=result.error_count,
        rejected_before_import=result.rejected_before_import,
        media_items_created=result.media_items_created,
        shows_created=result.shows_created,
        cursor_before=result.cursor_before,
        cursor_after=result.cursor_after,
    )
