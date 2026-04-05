from datetime import date, datetime
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


class HorrorfestAnalyticsYearRead(KlugORMModel):
    horrorfest_year: int
    watch_count: int
    watch_days: int
    new_watch_count: int
    rewatch_count: int
    total_runtime_seconds: int
    total_runtime_hours: Decimal
    average_watches_per_day: Decimal
    average_runtime_hours_per_day: Decimal
    average_runtime_minutes_per_watch: Decimal
    average_rating_value: Decimal | None = None
    rated_watch_count: int
    first_watch_at: datetime | None = None
    latest_watch_at: datetime | None = None


class HorrorfestAnalyticsDailyRead(KlugORMModel):
    watch_date: date
    watch_count: int
    total_runtime_seconds: int
    total_runtime_hours: Decimal
    average_rating_value: Decimal | None = None


class HorrorfestAnalyticsSourceRead(KlugORMModel):
    playback_source: str
    watch_count: int
    total_runtime_seconds: int
    total_runtime_hours: Decimal
    average_rating_value: Decimal | None = None


class HorrorfestAnalyticsRatingRead(KlugORMModel):
    rating_value: Decimal
    watch_count: int


class HorrorfestAnalyticsYearDetailRead(KlugORMModel):
    summary: HorrorfestAnalyticsYearRead
    daily_rows: list[HorrorfestAnalyticsDailyRead]
    source_rows: list[HorrorfestAnalyticsSourceRead]
    rating_rows: list[HorrorfestAnalyticsRatingRead]


class HorrorfestAnalyticsTitleMatrixRowRead(KlugORMModel):
    media_item_id: UUID | None = None
    title: str
    total_count: int
    year_counts: dict[str, int]


class HorrorfestAnalyticsDecadeMatrixRowRead(KlugORMModel):
    decade: str
    total_count: int
    year_counts: dict[str, int]


class HorrorfestAnalyticsTitleMatrixRead(KlugORMModel):
    years: list[int]
    rows: list[HorrorfestAnalyticsTitleMatrixRowRead]


class HorrorfestAnalyticsDecadeMatrixRead(KlugORMModel):
    years: list[int]
    rows: list[HorrorfestAnalyticsDecadeMatrixRowRead]


class HorrorfestAnalyticsComparisonDeltaRead(KlugORMModel):
    watch_count: int
    watch_days: int
    new_watch_count: int
    rewatch_count: int
    total_runtime_seconds: int
    total_runtime_hours: Decimal
    average_watches_per_day: Decimal
    average_runtime_hours_per_day: Decimal
    average_runtime_minutes_per_watch: Decimal
    average_rating_value: Decimal | None = None
    rated_watch_count: int


class HorrorfestAnalyticsComparisonSourceRead(KlugORMModel):
    playback_source: str
    left_watch_count: int
    right_watch_count: int
    delta_watch_count: int
    left_total_runtime_hours: Decimal
    right_total_runtime_hours: Decimal
    delta_total_runtime_hours: Decimal


class HorrorfestAnalyticsComparisonRatingRead(KlugORMModel):
    rating_value: Decimal
    left_watch_count: int
    right_watch_count: int
    delta_watch_count: int


class HorrorfestAnalyticsComparisonRepeatedTitleRead(KlugORMModel):
    media_item_id: UUID | None = None
    title: str
    total_count: int
    left_year_count: int
    right_year_count: int
    delta_count: int


class HorrorfestAnalyticsComparisonRead(KlugORMModel):
    left_year: int
    right_year: int
    left_summary: HorrorfestAnalyticsYearRead
    right_summary: HorrorfestAnalyticsYearRead
    delta: HorrorfestAnalyticsComparisonDeltaRead
    source_rows: list[HorrorfestAnalyticsComparisonSourceRead]
    rating_rows: list[HorrorfestAnalyticsComparisonRatingRead]
    repeated_title_rows: list[HorrorfestAnalyticsComparisonRepeatedTitleRead]


class HorrorfestAnalyticsHighestRatedRowRead(KlugORMModel):
    media_item_id: UUID | None = None
    title: str
    total_count: int
    average_rating_value: Decimal | None = None
    rated_watch_count: int


class HorrorfestAnalyticsHighestRatedLeaderboardRead(KlugORMModel):
    rows: list[HorrorfestAnalyticsHighestRatedRowRead]


class HorrorfestAnalyticsRewatchRowRead(KlugORMModel):
    media_item_id: UUID | None = None
    title: str
    total_count: int
    rewatch_count: int
    new_watch_count: int


class HorrorfestAnalyticsRewatchLeaderboardRead(KlugORMModel):
    rows: list[HorrorfestAnalyticsRewatchRowRead]


class HorrorfestAnalyticsCurationRowRead(KlugORMModel):
    media_item_id: UUID | None = None
    title: str
    total_count: int
    years_seen: int
    first_year: int
    latest_year: int
    current_streak_length: int = 0
    longest_streak_length: int | None = None
    streak_start_year: int | None = None
    streak_end_year: int | None = None
    gap_years: int | None = None
    gap_start_year: int | None = None
    gap_end_year: int | None = None
    years_since_last_seen: int | None = None


class HorrorfestAnalyticsCurationReportRead(KlugORMModel):
    rows: list[HorrorfestAnalyticsCurationRowRead]
