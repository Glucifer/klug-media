from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ShowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    show_id: UUID
    tmdb_id: int
    tvdb_id: int | None
    imdb_id: str | None
    title: str
    year: int | None
    created_at: datetime
    updated_at: datetime


class ShowProgressRead(BaseModel):
    show_id: UUID
    show_tmdb_id: int
    show_title: str
    user_id: UUID
    total_episodes: int
    watched_episodes: int
    watched_percent: Decimal


class ShowEpisodeRead(BaseModel):
    media_item_id: UUID
    title: str
    season_number: int | None
    episode_number: int | None
    watched_count: int
    watched_by_user: bool | None


class ShowDetailRead(BaseModel):
    show: ShowRead
    progress: list[ShowProgressRead]
    episodes: list[ShowEpisodeRead]
