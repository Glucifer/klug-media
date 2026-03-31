from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.metadata_enrichment import (
    MetadataEnrichmentBatchResult,
    MetadataEnrichmentItemRead,
)
from app.services.media_enrichment import MediaEnrichmentService

router = APIRouter(
    prefix="/metadata-enrichment",
    tags=["metadata-enrichment"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("/items", response_model=list[MetadataEnrichmentItemRead])
def list_metadata_enrichment_items(
    enrichment_status: str | None = Query(default=None),
    missing_ids_only: bool = Query(default=False),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[MetadataEnrichmentItemRead]:
    rows = MediaEnrichmentService.list_queue(
        session,
        enrichment_status=enrichment_status,
        missing_ids_only=missing_ids_only,
        limit=limit,
        offset=offset,
    )
    return [MediaEnrichmentService.build_queue_item(row) for row in rows]


@router.post(
    "/process-pending",
    response_model=MetadataEnrichmentBatchResult,
    status_code=status.HTTP_200_OK,
)
def process_pending_metadata_items(
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_db_session),
) -> MetadataEnrichmentBatchResult:
    results = MediaEnrichmentService.process_pending_items(session, limit=limit)
    items = [MediaEnrichmentService.build_queue_item(result.media_item) for result in results]
    return MetadataEnrichmentBatchResult(processed_count=len(items), items=items)


@router.post(
    "/items/{media_item_id}/retry",
    response_model=MetadataEnrichmentItemRead,
    status_code=status.HTTP_200_OK,
)
def retry_metadata_enrichment(
    media_item_id: UUID,
    session: Session = Depends(get_db_session),
) -> MetadataEnrichmentItemRead:
    try:
        result = MediaEnrichmentService.retry_media_item(
            session,
            media_item_id=media_item_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return MediaEnrichmentService.build_queue_item(result.media_item)
