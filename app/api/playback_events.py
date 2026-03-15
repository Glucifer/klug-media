from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.playback_events import PlaybackEventRead
from app.services.playback_events import PlaybackEventNotFoundError, PlaybackEventService

router = APIRouter(
    prefix="/playback-events",
    tags=["playback-events"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("", response_model=list[PlaybackEventRead])
def list_playback_events(
    user_id: UUID | None = Query(default=None),
    playback_source: str | None = Query(default=None),
    collector: str | None = Query(default=None),
    session_key: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    media_type: Literal["movie", "show", "episode"] | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[PlaybackEventRead]:
    playback_events = PlaybackEventService.list_playback_events(
        session,
        user_id=user_id,
        playback_source=playback_source,
        collector=collector,
        session_key=session_key,
        event_type=event_type,
        media_type=media_type,
        decision_status=decision_status,
        limit=limit,
        offset=offset,
    )
    return [PlaybackEventRead.model_validate(playback_event) for playback_event in playback_events]


@router.get("/{playback_event_id}", response_model=PlaybackEventRead)
def get_playback_event(
    playback_event_id: UUID,
    session: Session = Depends(get_db_session),
) -> PlaybackEventRead:
    try:
        playback_event = PlaybackEventService.get_playback_event(
            session,
            playback_event_id=playback_event_id,
        )
    except PlaybackEventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return PlaybackEventRead.model_validate(playback_event)
