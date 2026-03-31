from datetime import date, datetime
from uuid import UUID

from app.schemas.base import KlugORMModel
from app.schemas.media_items import MediaItemType


class MetadataEnrichmentItemRead(KlugORMModel):
    media_item_id: UUID
    type: MediaItemType
    title: str
    year: int | None
    summary: str | None
    poster_url: str | None
    release_date: date | None
    tmdb_id: int | None
    imdb_id: str | None
    tvdb_id: int | None
    show_tmdb_id: int | None
    season_number: int | None
    episode_number: int | None
    metadata_source: str | None
    metadata_updated_at: datetime | None
    base_runtime_seconds: int | None
    enrichment_status: str
    enrichment_error: str | None
    enrichment_attempted_at: datetime | None
    created_at: datetime


class MetadataEnrichmentBatchResult(KlugORMModel):
    processed_count: int
    items: list[MetadataEnrichmentItemRead]
