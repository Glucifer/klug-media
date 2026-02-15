from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import User


def list_users(session: Session) -> list[User]:
    statement = select(User).order_by(User.created_at.asc())
    return list(session.scalars(statement))


def create_user(session: Session, username: str) -> User:
    user = User(username=username)
    session.add(user)
    session.flush()
    session.refresh(user)
    return user
