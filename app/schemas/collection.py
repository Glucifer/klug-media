from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import KlugBaseModel


class JellyfinCollectionImportRequest(KlugBaseModel):
    dry_run: bool = False
    library_ids: list[str] | None = None
    notes: str | None = None


class JellyfinCollectionImportResponse(KlugBaseModel):
    import_batch_id: UUID
    status: str
    dry_run: bool
    processed_count: int
    inserted_count: int
    updated_count: int
    missing_marked_count: int
    skipped_count: int
    error_count: int
    media_items_created: int = 0
    shows_created: int = 0
    collection_entries_created: int = 0


class CollectionMovieRead(KlugBaseModel):
    collection_entry_id: UUID
    source: str
    source_item_id: str
    media_item_id: UUID
    title: str
    year: int | None
    tmdb_id: int | None
    imdb_id: str | None
    tvdb_id: int | None
    is_present: bool
    first_seen_at: datetime
    last_seen_at: datetime
    missing_since: datetime | None
    library_id: str
    library_name: str | None
    added_at: datetime | None
    runtime_seconds: int | None
    file_path: str | None


class CollectionShowRead(KlugBaseModel):
    collection_entry_id: UUID
    source: str
    source_item_id: str
    show_id: UUID
    title: str
    year: int | None
    tmdb_id: int | None
    imdb_id: str | None
    tvdb_id: int | None
    is_present: bool
    first_seen_at: datetime
    last_seen_at: datetime
    missing_since: datetime | None
    library_id: str
    library_name: str | None
    added_at: datetime | None
    runtime_seconds: int | None
    file_path: str | None


class CollectionEpisodeRead(KlugBaseModel):
    collection_entry_id: UUID
    source: str
    source_item_id: str
    media_item_id: UUID
    show_id: UUID | None
    show_title: str | None
    title: str
    season_number: int | None
    episode_number: int | None
    year: int | None
    tmdb_id: int | None
    imdb_id: str | None
    tvdb_id: int | None
    is_present: bool
    first_seen_at: datetime
    last_seen_at: datetime
    missing_since: datetime | None
    library_id: str
    library_name: str | None
    added_at: datetime | None
    runtime_seconds: int | None
    file_path: str | None


class CollectionListParams(KlugBaseModel):
    query: str | None = Field(default=None, min_length=1, max_length=200)
    present: bool | None = None
    limit: int = Field(default=25, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
