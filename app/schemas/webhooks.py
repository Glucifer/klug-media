from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.base import KlugBaseModel


class KodiScrobblePayload(KlugBaseModel):
    user_id: UUID
    media_type: Literal["movie", "episode"]
    title: str = Field(min_length=1, max_length=500)
    year: int | None = Field(default=None, ge=1800, le=3000)
    season: int | None = Field(default=None, ge=0)
    episode: int | None = Field(default=None, ge=0)
    tmdb_id: int | None = None
    imdb_id: str | None = None
    tvdb_id: int | None = None
    progress_percent: Decimal | None = Field(default=None, ge=0, le=100)
    playback_source: str = Field(default="Kodi", min_length=1, max_length=100)
