from datetime import date
from datetime import datetime
from decimal import Decimal
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


class MediaItemRelatedShowRead(KlugBaseModel):
    show_id: UUID
    title: str
    year: int | None
    tmdb_id: int
    tvdb_id: int | None
    imdb_id: str | None


class MediaItemRecentWatchRead(KlugBaseModel):
    watch_id: UUID
    user_id: UUID
    watched_at: datetime
    watched_at_local: datetime
    user_timezone: str
    playback_source: str
    completed: bool
    rewatch: bool
    rating_value: Decimal | None = None
    rating_scale: str | None = None
    watch_version_name: str | None = None
    watch_runtime_seconds: int | None = None
    effective_runtime_seconds: int | None = None
    display_title: str
    horrorfest_year: int | None = None
    horrorfest_watch_order: int | None = None
    is_horrorfest_watch: bool = False


class MediaItemDetailRead(KlugBaseModel):
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
    enrichment_attempted_at: datetime | None = None
    created_at: datetime
    show: MediaItemRelatedShowRead | None = None
    watch_count: int
    completed_watch_count: int
    latest_watch_at: datetime | None = None
    latest_rating_value: Decimal | None = None
    latest_rating_scale: str | None = None
    recent_watches: list[MediaItemRecentWatchRead]
