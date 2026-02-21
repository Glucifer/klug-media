from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.users import UserCreate, UserRead
from app.services.users import UserAlreadyExistsError, UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("", response_model=list[UserRead])
def list_users(session: Session = Depends(get_db_session)) -> list[UserRead]:
    users = UserService.list_users(session)
    return [UserRead.model_validate(user) for user in users]


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_db_session),
) -> UserRead:
    try:
        user = UserService.create_user(session, payload.username)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{exc.args[0]}' already exists",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return UserRead.model_validate(user)
