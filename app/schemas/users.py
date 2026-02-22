from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import KlugBaseModel, KlugORMModel


class UserCreate(KlugBaseModel):
    username: str = Field(min_length=1, max_length=100)
    timezone: str = Field(default="UTC", min_length=1, max_length=100)


class UserRead(KlugORMModel):
    user_id: UUID
    username: str
    timezone: str
    created_at: datetime
