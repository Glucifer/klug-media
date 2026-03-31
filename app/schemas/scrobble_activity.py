from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.schemas.base import KlugORMModel


class ScrobbleActivityRead(KlugORMModel):
    playback_event_id: UUID
    occurred_at: datetime
    user_id: UUID
    username: str | None = None
    collector: str
    playback_source: str
    event_type: str
    media_type: str
    guessed_title: str
    year: int | None = None
    season_number: int | None = None
    episode_number: int | None = None
    tmdb_id: int | None = None
    imdb_id: str | None = None
    tvdb_id: int | None = None
    progress_percent: Decimal | None = None
    decision_status: str | None = None
    decision_reason: str | None = None
    watch_id: UUID | None = None
    media_item_id: UUID | None = None
    origin_kind: str | None = None
    matched_title: str | None = None
    matched_media_type: str | None = None
    result_label: str = Field(default="")
    is_unmatched: bool = False
