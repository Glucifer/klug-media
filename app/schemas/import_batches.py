from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ImportBatchStartRequest(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    source_detail: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class ImportBatchFinishRequest(BaseModel):
    status: str = Field(min_length=1, max_length=30)
    watch_events_inserted: int = Field(default=0, ge=0)
    media_items_inserted: int = Field(default=0, ge=0)
    media_versions_inserted: int = Field(default=0, ge=0)
    tags_added: int = Field(default=0, ge=0)
    errors_count: int = Field(default=0, ge=0)
    notes: str | None = None


class ImportBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    import_batch_id: UUID
    source: str
    source_detail: str | None
    started_at: datetime
    finished_at: datetime | None
    status: str
    watch_events_inserted: int
    media_items_inserted: int
    media_versions_inserted: int
    tags_added: int
    errors_count: int
    notes: str | None


class ImportBatchErrorCreateRequest(BaseModel):
    severity: str = Field(default="error", min_length=1, max_length=20)
    entity_type: str | None = Field(default=None, max_length=100)
    entity_ref: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=1)
    details: dict = Field(default_factory=dict)


class ImportBatchErrorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    import_batch_error_id: UUID
    import_batch_id: UUID
    occurred_at: datetime
    severity: str
    entity_type: str | None
    entity_ref: str | None
    message: str
    details: dict
