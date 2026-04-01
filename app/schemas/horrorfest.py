from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AwareDatetime, Field

from app.schemas.base import KlugBaseModel, KlugORMModel


class HorrorfestYearUpsert(KlugBaseModel):
    window_start_at: AwareDatetime
    window_end_at: AwareDatetime
    label: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class HorrorfestYearRead(KlugORMModel):
    horrorfest_year: int
    window_start_at: datetime
    window_end_at: datetime
    label: str | None = None
    notes: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
    entry_count: int = 0
    total_runtime_seconds: int = 0
    average_rating_value: Decimal | None = None


class HorrorfestEntryRead(KlugORMModel):
    horrorfest_entry_id: UUID
    watch_id: UUID
    horrorfest_year: int
    watch_order: int | None = None
    source_kind: str
    created_at: datetime
    updated_at: datetime | None = None
    updated_by: str | None = None
    update_reason: str | None = None
    is_removed: bool = False
    removed_at: datetime | None = None
    removed_by: str | None = None
    removed_reason: str | None = None
    user_id: UUID
    media_item_id: UUID
    watched_at: datetime
    playback_source: str
    media_item_title: str
    media_item_type: str
    display_title: str
    rating_value: Decimal | None = None
    rating_scale: str | None = None
    effective_runtime_seconds: int | None = None
    rewatch: bool
    completed: bool


class HorrorfestEntryMutation(KlugBaseModel):
    updated_by: str = Field(min_length=1, max_length=100)
    update_reason: str | None = Field(default=None, max_length=500)


class HorrorfestEntryMove(HorrorfestEntryMutation):
    target_order: int = Field(ge=1, le=10000)


class HorrorfestEntryInclude(HorrorfestEntryMutation):
    horrorfest_year: int = Field(ge=1900, le=9999)
    target_order: int | None = Field(default=None, ge=1, le=10000)
