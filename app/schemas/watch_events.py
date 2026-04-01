from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AwareDatetime, Field

from app.schemas.base import KlugBaseModel, KlugORMModel


class WatchEventCreate(KlugBaseModel):
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
    created_by: str | None = Field(default=None, max_length=100)


class WatchEventRead(KlugORMModel):
    watch_id: UUID
    user_id: UUID
    media_item_id: UUID
    watched_at: datetime
    playback_source: str
    total_seconds: int | None
    watched_seconds: int | None
    progress_percent: Decimal | None
    watch_version_name: str | None = None
    watch_runtime_seconds: int | None = None
    effective_runtime_seconds: int | None = None
    completed: bool
    rating_value: Decimal | None
    rating_scale: str | None
    media_version_id: UUID | None
    import_batch_id: UUID | None
    origin_kind: str
    origin_playback_event_id: UUID | None
    created_at: datetime
    updated_at: datetime | None = None
    updated_by: str | None = None
    update_reason: str | None = None
    rewatch: bool
    is_deleted: bool = False
    deleted_at: datetime | None = None
    deleted_by: str | None = None
    deleted_reason: str | None = None
    dedupe_hash: str | None
    created_by: str | None
    source_event_id: str | None


class WatchEventListRead(WatchEventRead):
    media_item_title: str | None = None
    media_item_type: str | None = None
    media_item_season_number: int | None = None
    media_item_episode_number: int | None = None
    display_title: str | None = None
    watched_at_local: datetime | None = None
    user_timezone: str | None = None


class WatchEventDelete(KlugBaseModel):
    updated_by: str = Field(min_length=1, max_length=100)
    update_reason: str | None = Field(default=None, max_length=500)


class WatchEventRestore(KlugBaseModel):
    updated_by: str = Field(min_length=1, max_length=100)
    update_reason: str | None = Field(default=None, max_length=500)


class WatchEventCorrect(KlugBaseModel):
    updated_by: str = Field(min_length=1, max_length=100)
    update_reason: str | None = Field(default=None, max_length=500)
    watched_at: AwareDatetime | None = None
    media_item_id: UUID | None = None
    completed: bool | None = None
    rewatch: bool | None = None


class WatchEventRate(KlugBaseModel):
    updated_by: str = Field(min_length=1, max_length=100)
    update_reason: str | None = Field(default=None, max_length=500)
    rating_value: int = Field(ge=1, le=10)


class WatchEventVersionOverride(KlugBaseModel):
    updated_by: str = Field(min_length=1, max_length=100)
    update_reason: str | None = Field(default=None, max_length=500)
    version_name: str | None = Field(default=None, max_length=100)
    runtime_minutes: int | None = Field(default=None, ge=1, le=1000)
    clear_override: bool = False
