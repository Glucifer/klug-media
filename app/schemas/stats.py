from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.schemas.base import KlugORMModel


class StatsSummaryRead(KlugORMModel):
    user_id: UUID | None = None
    total_active_watches: int
    total_completed_watches: int
    total_rewatches: int
    total_watch_time_seconds: int
    total_watch_time_hours: Decimal
    movie_watch_count: int
    episode_watch_count: int
    average_rating_value: Decimal | None = None
    unrated_completed_watch_count: int


class StatsMonthlyRead(KlugORMModel):
    user_id: UUID | None = None
    year: int
    month: int
    watch_count: int
    movie_count: int
    episode_count: int
    rewatch_count: int
    rated_watch_count: int
    total_runtime_seconds: int
    average_rating_value: Decimal | None = None


class StatsHorrorfestRead(KlugORMModel):
    user_id: UUID | None = None
    horrorfest_year: int
    entry_count: int
    total_runtime_seconds: int
    total_runtime_hours: Decimal
    average_rating_value: Decimal | None = None
    rated_entry_count: int
    rewatch_count: int
    first_watch_at: datetime | None = None
    latest_watch_at: datetime | None = None
