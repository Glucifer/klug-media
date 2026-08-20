from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.jellyfin_integration import (
    JellyfinWebhookIngestRead,
    JellyfinWebhookPayload,
)
from app.services.playback_events import PlaybackEventConstraintError
from app.services.jellyfin_webhooks import JellyfinWebhookService
from app.services.watch_events import WatchEventConstraintError


router = APIRouter(
    prefix="/webhooks/jellyfin",
    tags=["webhooks", "jellyfin"],
    dependencies=[Depends(require_request_auth)],
)


@router.post(
    "/events",
    response_model=JellyfinWebhookIngestRead,
    status_code=status.HTTP_201_CREATED,
)
def ingest_jellyfin_event(
    payload: JellyfinWebhookPayload,
    session: Session = Depends(get_db_session),
) -> JellyfinWebhookIngestRead:
    try:
        result = JellyfinWebhookService.ingest(session, payload=payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except (PlaybackEventConstraintError, WatchEventConstraintError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return JellyfinWebhookIngestRead.model_validate(
        {
            "action": result.action,
            "reason": result.reason,
            "playback_event": result.playback_event,
            "watch_event": result.watch_event,
        }
    )
