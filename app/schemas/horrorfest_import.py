from datetime import UTC, date, datetime, time
from decimal import Decimal
from pydantic import Field

from app.schemas.base import KlugBaseModel


class HorrorfestPreserveRow(KlugBaseModel):
    trakt_log_id: str = Field(min_length=1, max_length=255)
    watched_at: date
    rewatch: bool = False
    watch_order: int = Field(ge=1)
    alternate_version: str | None = Field(default=None, max_length=50)
    watch_rating: Decimal | None = Field(default=None, ge=1, le=10)
    watch_year: int = Field(ge=1900, le=9999)
    movie_id: int | None = None
    tmdb_id: int = Field(ge=1)
    origin_country: str | None = Field(default=None, max_length=100)
    original_language: str | None = Field(default=None, max_length=100)
    runtime_used: int | None = Field(default=None, ge=1)

    def watched_at_start_utc(self) -> datetime:
        return datetime.combine(self.watched_at, time.min, tzinfo=UTC)

    def watched_at_end_utc(self) -> datetime:
        return datetime.combine(self.watched_at, time.max, tzinfo=UTC)


class HorrorfestPreserveImportSummary(KlugBaseModel):
    processed_count: int
    matched_count: int
    updated_count: int
    error_count: int
    year_configs_created: int = 0
    unmatched_rows: list[dict] = Field(default_factory=list)
