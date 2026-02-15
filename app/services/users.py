from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.entities import User
from app.repositories import users as user_repository


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a duplicate username."""


class UserService:
    @staticmethod
    def list_users(session: Session) -> list[User]:
        return user_repository.list_users(session)

    @staticmethod
    def create_user(session: Session, username: str) -> User:
        normalized_username = username.strip()
        if not normalized_username:
            raise ValueError("Username must not be empty")

        try:
            user = user_repository.create_user(session, normalized_username)
            session.commit()
            return user
        except IntegrityError as exc:
            session.rollback()
            raise UserAlreadyExistsError(normalized_username) from exc
