from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.watch_events import WatchEventCreate, WatchEventRead
from app.services.watch_events import WatchEventConstraintError, WatchEventService

router = APIRouter(
    prefix="/watch-events",
    tags=["watch-events"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("", response_model=list[WatchEventRead])
def list_watch_events(
    user_id: UUID | None = Query(default=None),
    media_item_id: UUID | None = Query(default=None),
    watched_after: datetime | None = Query(default=None),
    watched_before: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    session: Session = Depends(get_db_session),
) -> list[WatchEventRead]:
    watch_events = WatchEventService.list_watch_events(
        session,
        user_id=user_id,
        media_item_id=media_item_id,
        watched_after=watched_after,
        watched_before=watched_before,
        limit=limit,
    )
    return [WatchEventRead.model_validate(item) for item in watch_events]


@router.post("", response_model=WatchEventRead, status_code=status.HTTP_201_CREATED)
def create_watch_event(
    payload: WatchEventCreate,
    session: Session = Depends(get_db_session),
) -> WatchEventRead:
    try:
        watch_event = WatchEventService.create_watch_event(
            session,
            user_id=payload.user_id,
            media_item_id=payload.media_item_id,
            watched_at=payload.watched_at,
            playback_source=payload.playback_source,
            total_seconds=payload.total_seconds,
            watched_seconds=payload.watched_seconds,
            progress_percent=payload.progress_percent,
            completed=payload.completed,
            rating_value=payload.rating_value,
            rating_scale=payload.rating_scale,
            media_version_id=payload.media_version_id,
            source_event_id=payload.source_event_id,
        )
    except WatchEventConstraintError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return WatchEventRead.model_validate(watch_event)
