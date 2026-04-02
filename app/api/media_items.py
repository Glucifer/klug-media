from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.media_items import MediaItemCreate, MediaItemDetailRead, MediaItemRead
from app.services.media_items import MediaItemAlreadyExistsError, MediaItemService

router = APIRouter(
    prefix="/media-items",
    tags=["media-items"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("", response_model=list[MediaItemRead])
def list_media_items(session: Session = Depends(get_db_session)) -> list[MediaItemRead]:
    media_items = MediaItemService.list_media_items(session)
    return [MediaItemRead.model_validate(item) for item in media_items]


@router.get("/{media_item_id}", response_model=MediaItemDetailRead)
def get_media_item_detail(
    media_item_id: UUID,
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> MediaItemDetailRead:
    detail = MediaItemService.get_media_item_detail(
        session,
        media_item_id=media_item_id,
        user_id=user_id,
    )
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media item '{media_item_id}' not found",
        )
    return MediaItemDetailRead.model_validate(detail)


@router.post("", response_model=MediaItemRead, status_code=status.HTTP_201_CREATED)
def create_media_item(
    payload: MediaItemCreate,
    session: Session = Depends(get_db_session),
) -> MediaItemRead:
    try:
        media_item = MediaItemService.create_media_item(
            session,
            media_type=payload.type.value,
            title=payload.title,
            year=payload.year,
            tmdb_id=payload.tmdb_id,
            imdb_id=payload.imdb_id,
            tvdb_id=payload.tvdb_id,
        )
    except MediaItemAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return MediaItemRead.model_validate(media_item)
