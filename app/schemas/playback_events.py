from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.base import KlugBaseModel, KlugORMModel
from app.schemas.watch_events import WatchEventRead


class PlaybackEventRead(KlugORMModel):
    playback_event_id: UUID
    collector: str
    playback_source: str
    event_type: str
    user_id: UUID
    occurred_at: datetime
    source_event_id: str | None
    session_key: str | None
    media_type: str
    title: str
    year: int | None
    season_number: int | None
    episode_number: int | None
    tmdb_id: int | None
    imdb_id: str | None
    tvdb_id: int | None
    progress_percent: Decimal | None
    payload: dict = Field(default_factory=dict)
    decision_status: str | None = None
    decision_reason: str | None = None
    watch_id: UUID | None = None
    created_at: datetime


class PlaybackEventIngestRead(KlugBaseModel):
    action: Literal[
        "recorded_only",
        "watch_event_created",
        "duplicate_watch_event_skipped",
    ]
    reason: str | None = None
    playback_event: PlaybackEventRead
    watch_event: WatchEventRead | None = None
