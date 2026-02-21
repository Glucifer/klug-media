from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WatchEventCreate(BaseModel):
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


class WatchEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    watch_id: UUID
    user_id: UUID
    media_item_id: UUID
    watched_at: datetime
    playback_source: str
    total_seconds: int | None
    watched_seconds: int | None
    progress_percent: Decimal | None
    completed: bool
    rating_value: Decimal | None
    rating_scale: str | None
    media_version_id: UUID | None
    import_batch_id: UUID | None
    created_at: datetime
    rewatch: bool
    dedupe_hash: str | None
    created_by: str | None
    source_event_id: str | None


class WatchEventListRead(WatchEventRead):
    media_item_title: str | None = None
    media_item_type: str | None = None
    media_item_season_number: int | None = None
    media_item_episode_number: int | None = None
    display_title: str | None = None
