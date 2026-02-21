from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.shows import ShowProgressRead, ShowRead
from app.services.shows import ShowService

router = APIRouter(prefix="/shows", tags=["shows"])


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
