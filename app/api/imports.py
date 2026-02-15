from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.imports import WatchEventImportRequest, WatchEventImportResponse
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
        processed_count=result.processed_count,
        inserted_count=result.inserted_count,
        error_count=result.error_count,
    )
