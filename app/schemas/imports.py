from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import AwareDatetime, Field

from app.schemas.base import KlugBaseModel


class ImportMode(str, Enum):
    bootstrap = "bootstrap"
    incremental = "incremental"


class ImportedWatchEvent(KlugBaseModel):
    user_id: UUID
    media_item_id: UUID
    watched_at: AwareDatetime
    playback_source: str = Field(min_length=1, max_length=100)
    total_seconds: int | None = Field(default=None, ge=0)
    watched_seconds: int | None = Field(default=None, ge=0)
    progress_percent: Decimal | None = Field(default=None, ge=0, le=100)
    completed: bool = True
    rating_value: Decimal | None = None
    rating_scale: str | None = Field(default=None, max_length=50)
    media_version_id: UUID | None = None
    source_event_id: str | None = Field(default=None, max_length=255)


class WatchEventImportRequest(KlugBaseModel):
    source: str = Field(min_length=1, max_length=100)
    mode: ImportMode
    dry_run: bool = False
    resume_from_latest: bool = False
    source_detail: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    rejected_before_import: int = Field(default=0, ge=0)
    media_items_created: int = Field(default=0, ge=0)
    shows_created: int = Field(default=0, ge=0)
    events: list[ImportedWatchEvent] = Field(min_length=1)


class WatchEventImportResponse(KlugBaseModel):
    import_batch_id: UUID
    status: str
    dry_run: bool
    processed_count: int
    inserted_count: int
    skipped_count: int
    error_count: int
    rejected_before_import: int = 0
    media_items_created: int = 0
    shows_created: int = 0
    cursor_before: dict | None = None
    cursor_after: dict | None = None


class LegacySourceWatchEventRow(KlugBaseModel):
    user_id: UUID
    media_item_id: UUID
    watched_at: AwareDatetime
    player: str = Field(min_length=1, max_length=100)
    total_seconds: int | None = Field(default=None, ge=0)
    watched_seconds: int | None = Field(default=None, ge=0)
    progress_percent: Decimal | None = Field(default=None, ge=0, le=100)
    completed: bool = True
    rating: Decimal | None = None
    media_version_id: UUID | None = None
    source_event_id: str | None = Field(default=None, max_length=255)


class LegacySourceWatchEventImportRequest(KlugBaseModel):
    mode: ImportMode
    dry_run: bool = False
    resume_from_latest: bool = False
    source_detail: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    rejected_before_import: int = Field(default=0, ge=0)
    media_items_created: int = Field(default=0, ge=0)
    shows_created: int = Field(default=0, ge=0)
    rows: list[LegacySourceWatchEventRow] = Field(min_length=1)
