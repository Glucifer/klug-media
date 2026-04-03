from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.schemas.base import KlugBaseModel


class LibraryMovieRead(KlugBaseModel):
    media_item_id: UUID
    title: str
    year: int | None
    watch_count: int
    latest_watched_at: datetime | None
    latest_rating_value: int | None
    latest_rating_scale: str | None
    enrichment_status: str


class LibraryEpisodeRead(KlugBaseModel):
    media_item_id: UUID
    show_id: UUID | None
    show_title: str | None
    season_number: int | None
    episode_number: int | None
    title: str
    watch_count: int
    latest_watched_at: datetime | None
    enrichment_status: str


class LibraryShowRead(KlugBaseModel):
    show_id: UUID
    media_item_id: UUID | None
    title: str
    year: int | None
    watched_episodes: int
    total_episodes: int
    watched_percent: Decimal
