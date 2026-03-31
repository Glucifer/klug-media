from datetime import date
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
    summary: str | None = None
    poster_url: str | None = None
    release_date: date | None = None
    tmdb_id: int | None
    imdb_id: str | None
    tvdb_id: int | None
    show_tmdb_id: int | None = None
    season_number: int | None = None
    episode_number: int | None = None
    metadata_source: str | None = None
    metadata_updated_at: datetime | None = None
    base_runtime_seconds: int | None = None
    enrichment_status: str
    enrichment_error: str | None = None
    failure_code: str | None = None
    next_action: str | None = None
    last_lookup_kind: str | None = None
    enrichment_attempted_at: datetime | None = None
    created_at: datetime
