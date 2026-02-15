from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ImportMode(str, Enum):
    bootstrap = "bootstrap"
    incremental = "incremental"


class ImportedWatchEvent(BaseModel):
    user_id: UUID
    media_item_id: UUID
    watched_at: datetime
    playback_source: str = Field(min_length=1, max_length=100)
    total_seconds: int | None = Field(default=None, ge=0)
    watched_seconds: int | None = Field(default=None, ge=0)
    progress_percent: Decimal | None = Field(default=None, ge=0, le=100)
    completed: bool = True
    rating_value: Decimal | None = None
    rating_scale: str | None = Field(default=None, max_length=50)
    media_version_id: UUID | None = None
    source_event_id: str | None = Field(default=None, max_length=255)


class WatchEventImportRequest(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    mode: ImportMode
    dry_run: bool = False
    resume_from_latest: bool = False
    source_detail: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    events: list[ImportedWatchEvent] = Field(min_length=1)


class WatchEventImportResponse(BaseModel):
    import_batch_id: UUID
    status: str
    dry_run: bool
    processed_count: int
    inserted_count: int
    skipped_count: int
    error_count: int
    cursor_before: dict | None = None
    cursor_after: dict | None = None


class LegacySourceWatchEventRow(BaseModel):
    user_id: UUID
    media_item_id: UUID
    watched_at: datetime
    player: str = Field(min_length=1, max_length=100)
    total_seconds: int | None = Field(default=None, ge=0)
    watched_seconds: int | None = Field(default=None, ge=0)
    progress_percent: Decimal | None = Field(default=None, ge=0, le=100)
    completed: bool = True
    rating: Decimal | None = None
    media_version_id: UUID | None = None
    source_event_id: str | None = Field(default=None, max_length=255)


class LegacySourceWatchEventImportRequest(BaseModel):
    mode: ImportMode
    dry_run: bool = False
    resume_from_latest: bool = False
    source_detail: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    rows: list[LegacySourceWatchEventRow] = Field(min_length=1)
