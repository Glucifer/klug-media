from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import AwareDatetime
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.watch_events import (
    WatchEventCorrect,
    WatchEventCreate,
    WatchEventDelete,
    WatchEventListRead,
    WatchEventRate,
    WatchEventRead,
    WatchEventRestore,
    WatchEventVersionOverride,
)
from app.services.watch_events import WatchEventConstraintError, WatchEventService

router = APIRouter(
    prefix="/watch-events",
    tags=["watch-events"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("", response_model=list[WatchEventListRead])
def list_watch_events(
    user_id: UUID | None = Query(default=None),
    media_item_id: UUID | None = Query(default=None),
    watched_after: AwareDatetime | None = Query(default=None),
    watched_before: AwareDatetime | None = Query(default=None),
    local_date_from: date | None = Query(default=None),
    local_date_to: date | None = Query(default=None),
    media_type: Literal["movie", "show", "episode"] | None = Query(default=None),
    include_deleted: bool = Query(default=False),
    deleted_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[WatchEventListRead]:
    watch_events = WatchEventService.list_watch_events(
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
        limit=limit,
        offset=offset,
    )
    return [WatchEventListRead.model_validate(item) for item in watch_events]


@router.get("/unrated", response_model=list[WatchEventListRead])
def list_unrated_watch_events(
    user_id: UUID | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[WatchEventListRead]:
    watch_events = WatchEventService.list_unrated_watch_events(
        session,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return [WatchEventListRead.model_validate(item) for item in watch_events]


@router.post("", response_model=WatchEventRead, status_code=status.HTTP_201_CREATED)
def create_watch_event(
    payload: WatchEventCreate,
    session: Session = Depends(get_db_session),
) -> WatchEventRead:
    try:
        result = WatchEventService.create_watch_event(
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
            created_by=payload.created_by,
            origin_kind="manual_entry",
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

    return WatchEventRead.model_validate(result.watch_event)


@router.post("/{watch_id}/delete", response_model=WatchEventRead)
def delete_watch_event(
    watch_id: UUID,
    payload: WatchEventDelete,
    session: Session = Depends(get_db_session),
) -> WatchEventRead:
    try:
        watch_event = WatchEventService.soft_delete_watch_event(
            session,
            watch_id=watch_id,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except WatchEventConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return WatchEventRead.model_validate(watch_event)


@router.post("/{watch_id}/restore", response_model=WatchEventRead)
def restore_watch_event(
    watch_id: UUID,
    payload: WatchEventRestore,
    session: Session = Depends(get_db_session),
) -> WatchEventRead:
    try:
        watch_event = WatchEventService.restore_watch_event(
            session,
            watch_id=watch_id,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except WatchEventConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return WatchEventRead.model_validate(watch_event)


@router.post("/{watch_id}/correct", response_model=WatchEventRead)
def correct_watch_event(
    watch_id: UUID,
    payload: WatchEventCorrect,
    session: Session = Depends(get_db_session),
) -> WatchEventRead:
    try:
        watch_event = WatchEventService.correct_watch_event(
            session,
            watch_id=watch_id,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
            watched_at=payload.watched_at,
            media_item_id=payload.media_item_id,
            completed=payload.completed,
            rewatch=payload.rewatch,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except WatchEventConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return WatchEventRead.model_validate(watch_event)


@router.post("/{watch_id}/rate", response_model=WatchEventRead)
def rate_watch_event(
    watch_id: UUID,
    payload: WatchEventRate,
    session: Session = Depends(get_db_session),
) -> WatchEventRead:
    try:
        watch_event = WatchEventService.rate_watch_event(
            session,
            watch_id=watch_id,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
            rating_value=payload.rating_value,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except WatchEventConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return WatchEventRead.model_validate(watch_event)


@router.post("/{watch_id}/version", response_model=WatchEventRead)
def set_watch_event_version_override(
    watch_id: UUID,
    payload: WatchEventVersionOverride,
    session: Session = Depends(get_db_session),
) -> WatchEventRead:
    try:
        watch_event = WatchEventService.set_watch_event_version_override(
            session,
            watch_id=watch_id,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
            version_name=payload.version_name,
            runtime_minutes=payload.runtime_minutes,
            clear_override=payload.clear_override,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except WatchEventConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return WatchEventRead.model_validate(watch_event)
