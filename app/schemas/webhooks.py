from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, Field

from app.schemas.base import KlugBaseModel


class KodiPlaybackEventPayload(KlugBaseModel):
    user_id: UUID
    event_type: Literal["play", "pause", "resume", "stop", "progress", "scrobble"] = (
        "scrobble"
    )
    occurred_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))
    source_event_id: str | None = Field(default=None, max_length=255)
    session_key: str | None = Field(default=None, max_length=255)
    media_type: Literal["movie", "episode"]
    title: str = Field(min_length=1, max_length=500)
    year: int | None = Field(default=None, ge=1800, le=3000)
    season: int | None = Field(default=None, ge=0)
    episode: int | None = Field(default=None, ge=0)
    tmdb_id: int | None = None
    imdb_id: str | None = None
    tvdb_id: int | None = None
    progress_percent: Decimal | None = Field(default=None, ge=0, le=100)
    playback_source: str = Field(default="kodi", min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)


class KodiScrobblePayload(KodiPlaybackEventPayload):
    event_type: Literal["scrobble"] = "scrobble"
