from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import User


def list_users(session: Session) -> list[User]:
    statement = select(User).order_by(User.created_at.asc())
    return list(session.scalars(statement))


def get_user_by_id(session: Session, user_id) -> User | None:
    statement = select(User).where(User.user_id == user_id)
    return session.scalar(statement)


def get_user_by_jellyfin_user_id(
    session: Session, *, jellyfin_user_id: UUID
) -> User | None:
    statement = select(User).where(User.jellyfin_user_id == jellyfin_user_id)
    return session.scalar(statement)


def create_user(session: Session, username: str, timezone: str) -> User:
    user = User(username=username, timezone=timezone)
    session.add(user)
    session.flush()
    session.refresh(user)
    return user


def update_jellyfin_user_mapping(
    session: Session,
    *,
    user: User,
    jellyfin_user_id: UUID | None,
) -> User:
    user.jellyfin_user_id = jellyfin_user_id
    session.add(user)
    session.flush()
    session.refresh(user)
    return user
