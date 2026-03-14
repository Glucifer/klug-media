from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.playback_events import PlaybackEventIngestRead
from app.schemas.watch_events import WatchEventRead
from app.schemas.webhooks import KodiScrobblePayload
from app.schemas.webhooks import KodiPlaybackEventPayload
from app.services.playback_events import (
    PlaybackEventConstraintError,
    PlaybackEventDuplicateError,
)
from app.services.watch_events import WatchEventConstraintError
from app.services.webhooks import WebhookService

router = APIRouter(
    prefix="/webhooks/kodi",
    tags=["webhooks", "kodi"],
    dependencies=[Depends(require_request_auth)],
)


@router.post(
    "/events",
    response_model=PlaybackEventIngestRead,
    status_code=status.HTTP_201_CREATED,
)
def ingest_kodi_playback_event(
    payload: KodiPlaybackEventPayload,
    session: Session = Depends(get_db_session),
) -> PlaybackEventIngestRead:
    try:
        result = WebhookService.ingest_kodi_playback_event(
            session,
            payload=payload,
        )
    except PlaybackEventDuplicateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (PlaybackEventConstraintError, WatchEventConstraintError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest playback event",
        ) from exc

    return PlaybackEventIngestRead.model_validate(
        {
            "action": result.action,
            "reason": result.reason,
            "playback_event": result.playback_event,
            "watch_event": result.watch_event,
        }
    )


@router.post(
    "/scrobble",
    response_model=WatchEventRead,
    status_code=status.HTTP_201_CREATED,
)
def scrobble_from_kodi(
    payload: KodiScrobblePayload,
    session: Session = Depends(get_db_session),
) -> WatchEventRead:
    try:
        watch_event = WebhookService.process_kodi_scrobble(
            session=session,
            user_id=payload.user_id,
            payload=payload,
        )
    except PlaybackEventDuplicateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (PlaybackEventConstraintError, WatchEventConstraintError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process scrobble",
        ) from exc

    return WatchEventRead.model_validate(watch_event)
