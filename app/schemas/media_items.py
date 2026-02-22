from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import Field

from app.schemas.base import KlugBaseModel, KlugORMModel


class MediaItemType(str, Enum):
    movie = "movie"
    show = "show"
    episode = "episode"


class MediaItemCreate(KlugBaseModel):
    type: MediaItemType
    title: str = Field(min_length=1, max_length=500)
    year: int | None = Field(default=None, ge=1800, le=3000)
    tmdb_id: int | None = None
    imdb_id: str | None = None
    tvdb_id: int | None = None


class MediaItemRead(KlugORMModel):
    media_item_id: UUID
    type: MediaItemType
    title: str
    year: int | None
    tmdb_id: int | None
    imdb_id: str | None
    tvdb_id: int | None
    created_at: datetime
