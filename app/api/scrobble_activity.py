from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.scrobble_activity import ScrobbleActivityRead
from app.services.scrobble_activity import ScrobbleActivityService

router = APIRouter(
    prefix="/scrobble-activity",
    tags=["scrobble-activity"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("", response_model=list[ScrobbleActivityRead])
def list_scrobble_activity(
    user_id: UUID | None = Query(default=None),
    collector: str | None = Query(default=None),
    playback_source: str | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    media_type: Literal["movie", "show", "episode"] | None = Query(default=None),
    occurred_after: datetime | None = Query(default=None),
    occurred_before: datetime | None = Query(default=None),
    only_unmatched: bool = Query(default=False),
    only_with_watch: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[ScrobbleActivityRead]:
    rows = ScrobbleActivityService.list_scrobble_activity(
        session,
        user_id=user_id,
        collector=collector,
        playback_source=playback_source,
        decision_status=decision_status,
        event_type=event_type,
        media_type=media_type,
        occurred_after=occurred_after,
        occurred_before=occurred_before,
        only_unmatched=only_unmatched,
        only_with_watch=only_with_watch,
        limit=limit,
        offset=offset,
    )
    return [ScrobbleActivityRead.model_validate(row) for row in rows]
