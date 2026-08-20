from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.models.entities import User
from app.repositories import users as user_repository


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a duplicate username."""


class JellyfinUserAlreadyMappedError(Exception):
    """Raised when a Jellyfin user is already mapped to another Klug user."""


class UserService:
    @staticmethod
    def list_users(session: Session) -> list[User]:
        return user_repository.list_users(session)

    @staticmethod
    def get_user_by_id(session: Session, user_id) -> User | None:
        return user_repository.get_user_by_id(session, user_id)

    @staticmethod
    def get_user_by_jellyfin_user_id(
        session: Session, *, jellyfin_user_id: UUID
    ) -> User | None:
        return user_repository.get_user_by_jellyfin_user_id(
            session,
            jellyfin_user_id=jellyfin_user_id,
        )

    @staticmethod
    def create_user(session: Session, username: str, timezone: str = "UTC") -> User:
        normalized_username = username.strip()
        if not normalized_username:
            raise ValueError("Username must not be empty")
        normalized_timezone = timezone.strip()
        if not normalized_timezone:
            raise ValueError("Timezone must not be empty")

        try:
            user = user_repository.create_user(
                session,
                normalized_username,
                normalized_timezone,
            )
            session.commit()
            return user
        except IntegrityError as exc:
            session.rollback()
            raise UserAlreadyExistsError(normalized_username) from exc

    @staticmethod
    def update_jellyfin_user_mapping(
        session: Session,
        *,
        user_id: UUID,
        jellyfin_user_id: UUID | None,
    ) -> User:
        user = user_repository.get_user_by_id(session, user_id)
        if user is None:
            raise ValueError(f"User '{user_id}' not found")

        try:
            updated = user_repository.update_jellyfin_user_mapping(
                session,
                user=user,
                jellyfin_user_id=jellyfin_user_id,
            )
            session.commit()
            return updated
        except IntegrityError as exc:
            session.rollback()
            raise JellyfinUserAlreadyMappedError(str(jellyfin_user_id)) from exc
