from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.jellyfin_integration import (
    JellyfinIntegrationStatusRead,
    JellyfinUserMappingRead,
    JellyfinUserMappingUpdate,
)
from app.services.jellyfin import JellyfinClientError, JellyfinConfigurationError
from app.services.jellyfin_integration import JellyfinIntegrationService
from app.services.users import JellyfinUserAlreadyMappedError, UserService


router = APIRouter(
    prefix="/integrations/jellyfin",
    tags=["integrations", "jellyfin"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("/status", response_model=JellyfinIntegrationStatusRead)
def get_jellyfin_status(
    session: Session = Depends(get_db_session),
) -> JellyfinIntegrationStatusRead:
    return JellyfinIntegrationStatusRead.model_validate(
        JellyfinIntegrationService.get_status(session),
        from_attributes=True,
    )


@router.get("/users", response_model=list[JellyfinUserMappingRead])
def list_jellyfin_users(
    session: Session = Depends(get_db_session),
) -> list[JellyfinUserMappingRead]:
    try:
        mappings = JellyfinIntegrationService.list_user_mappings(session)
    except JellyfinConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except JellyfinClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    return [
        JellyfinUserMappingRead.model_validate(mapping, from_attributes=True)
        for mapping in mappings
    ]


@router.put("/users/{klug_user_id}", response_model=JellyfinUserMappingUpdate)
def update_jellyfin_user_mapping(
    klug_user_id: UUID,
    payload: JellyfinUserMappingUpdate,
    session: Session = Depends(get_db_session),
) -> JellyfinUserMappingUpdate:
    try:
        user = UserService.update_jellyfin_user_mapping(
            session,
            user_id=klug_user_id,
            jellyfin_user_id=payload.jellyfin_user_id,
        )
    except JellyfinUserAlreadyMappedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Jellyfin user is already mapped to another Klug user",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return JellyfinUserMappingUpdate(jellyfin_user_id=user.jellyfin_user_id)
