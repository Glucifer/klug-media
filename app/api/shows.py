from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_api_key
from app.db.session import get_db_session
from app.schemas.shows import ShowDetailRead, ShowEpisodeRead, ShowProgressRead, ShowRead
from app.services.shows import ShowNotFoundError, ShowService

router = APIRouter(
    prefix="/shows",
    tags=["shows"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=list[ShowRead])
def list_shows(session: Session = Depends(get_db_session)) -> list[ShowRead]:
    shows = ShowService.list_shows(session)
    return [ShowRead.model_validate(show) for show in shows]


@router.get("/progress", response_model=list[ShowProgressRead])
def list_show_progress(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> list[ShowProgressRead]:
    rows = ShowService.list_show_progress(session, user_id=user_id)
    return [ShowProgressRead.model_validate(row) for row in rows]


@router.get("/{show_id}", response_model=ShowDetailRead)
def get_show_detail(
    show_id: UUID,
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> ShowDetailRead:
    try:
        detail = ShowService.get_show_detail(session, show_id=show_id, user_id=user_id)
    except ShowNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ShowDetailRead(
        show=ShowRead.model_validate(detail["show"]),
        progress=[ShowProgressRead.model_validate(row) for row in detail["progress"]],
        episodes=[ShowEpisodeRead.model_validate(row) for row in detail["episodes"]],
    )
