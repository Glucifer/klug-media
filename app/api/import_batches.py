from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_api_key
from app.db.session import get_db_session
from app.schemas.import_batches import (
    ImportBatchErrorCreateRequest,
    ImportBatchErrorRead,
    ImportBatchFinishRequest,
    ImportBatchRead,
    ImportBatchStartRequest,
)
from app.services.import_batches import (
    ImportBatchConstraintError,
    ImportBatchNotFoundError,
    ImportBatchService,
)

router = APIRouter(prefix="/import-batches", tags=["import-batches"])


@router.get("", response_model=list[ImportBatchRead])
def list_import_batches(
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db_session),
) -> list[ImportBatchRead]:
    batches = ImportBatchService.list_import_batches(session, limit=limit)
    return [ImportBatchRead.model_validate(batch) for batch in batches]


@router.get("/{import_batch_id}", response_model=ImportBatchRead)
def get_import_batch(
    import_batch_id: UUID,
    session: Session = Depends(get_db_session),
) -> ImportBatchRead:
    try:
        batch = ImportBatchService.get_import_batch(
            session, import_batch_id=import_batch_id
        )
    except ImportBatchNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return ImportBatchRead.model_validate(batch)


@router.post("", response_model=ImportBatchRead, status_code=status.HTTP_201_CREATED)
def start_import_batch(
    payload: ImportBatchStartRequest,
    _: None = Depends(require_api_key),
    session: Session = Depends(get_db_session),
) -> ImportBatchRead:
    try:
        batch = ImportBatchService.start_import_batch(
            session,
            source=payload.source,
            source_detail=payload.source_detail,
            notes=payload.notes,
        )
    except ImportBatchConstraintError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ImportBatchRead.model_validate(batch)


@router.post("/{import_batch_id}/finish", response_model=ImportBatchRead)
def finish_import_batch(
    import_batch_id: UUID,
    payload: ImportBatchFinishRequest,
    _: None = Depends(require_api_key),
    session: Session = Depends(get_db_session),
) -> ImportBatchRead:
    try:
        batch = ImportBatchService.finish_import_batch(
            session,
            import_batch_id=import_batch_id,
            status=payload.status,
            watch_events_inserted=payload.watch_events_inserted,
            media_items_inserted=payload.media_items_inserted,
            media_versions_inserted=payload.media_versions_inserted,
            tags_added=payload.tags_added,
            errors_count=payload.errors_count,
            notes=payload.notes,
        )
    except ImportBatchNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ImportBatchConstraintError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ImportBatchRead.model_validate(batch)


@router.get("/{import_batch_id}/errors", response_model=list[ImportBatchErrorRead])
def list_import_batch_errors(
    import_batch_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    session: Session = Depends(get_db_session),
) -> list[ImportBatchErrorRead]:
    try:
        errors = ImportBatchService.list_import_batch_errors(
            session,
            import_batch_id=import_batch_id,
            limit=limit,
        )
    except ImportBatchNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return [ImportBatchErrorRead.model_validate(error) for error in errors]


@router.post(
    "/{import_batch_id}/errors",
    response_model=ImportBatchErrorRead,
    status_code=status.HTTP_201_CREATED,
)
def add_import_batch_error(
    import_batch_id: UUID,
    payload: ImportBatchErrorCreateRequest,
    _: None = Depends(require_api_key),
    session: Session = Depends(get_db_session),
) -> ImportBatchErrorRead:
    try:
        error = ImportBatchService.add_import_batch_error(
            session,
            import_batch_id=import_batch_id,
            severity=payload.severity,
            entity_type=payload.entity_type,
            entity_ref=payload.entity_ref,
            message=payload.message,
            details=payload.details,
        )
    except ImportBatchNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ImportBatchConstraintError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ImportBatchErrorRead.model_validate(error)
