from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_api_key
from app.db.session import get_db_session
from app.schemas.media_items import MediaItemCreate, MediaItemRead
from app.services.media_items import MediaItemAlreadyExistsError, MediaItemService

router = APIRouter(prefix="/media-items", tags=["media-items"])


@router.get("", response_model=list[MediaItemRead])
def list_media_items(session: Session = Depends(get_db_session)) -> list[MediaItemRead]:
    media_items = MediaItemService.list_media_items(session)
    return [MediaItemRead.model_validate(item) for item in media_items]


@router.post("", response_model=MediaItemRead, status_code=status.HTTP_201_CREATED)
def create_media_item(
    payload: MediaItemCreate,
    _: None = Depends(require_api_key),
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
