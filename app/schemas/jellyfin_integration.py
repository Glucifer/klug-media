from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, Field, field_validator, model_validator

from app.schemas.base import KlugBaseModel
from app.schemas.playback_events import PlaybackEventRead
from app.schemas.watch_events import WatchEventRead
from app.services.jellyfin import normalize_jellyfin_item_id


class JellyfinUserMappingUpdate(KlugBaseModel):
    jellyfin_user_id: UUID | None


class JellyfinUserMappingRead(KlugBaseModel):
    jellyfin_user_id: UUID
    jellyfin_username: str
    klug_user_id: UUID | None = None
    klug_username: str | None = None


class JellyfinIntegrationStatusRead(KlugBaseModel):
    configured: bool
    connected: bool
    connection_error: str | None = None
    mapped_user_count: int
    latest_webhook_at: datetime | None = None
    latest_webhook_decision: str | None = None
    latest_reconciliation_at: datetime | None = None
    latest_reconciliation_status: str | None = None


class JellyfinWebhookPayload(KlugBaseModel):
    notification_type: Literal["PlaybackStart", "PlaybackStop"]
    server_id: str = Field(min_length=1, max_length=100)
    occurred_at: AwareDatetime
    jellyfin_user_id: UUID
    item_id: str
    item_type: Literal["Movie", "Episode"]
    title: str = Field(min_length=1, max_length=500)
    series_name: str | None = Field(default=None, max_length=500)
    year: int | None = Field(default=None, ge=1800, le=3000)
    season_number: int | None = Field(default=None, ge=0)
    episode_number: int | None = Field(default=None, ge=0)
    runtime_ticks: int | None = Field(default=None, ge=0)
    playback_position_ticks: int | None = Field(default=None, ge=0)
    played_to_completion: bool = False
    device_id: str | None = Field(default=None, max_length=255)
    device_name: str | None = Field(default=None, max_length=255)
    client_name: str | None = Field(default=None, max_length=255)
    media_source_id: str | None = Field(default=None, max_length=255)
    tmdb_id: int | None = None
    imdb_id: str | None = Field(default=None, max_length=50)
    tvdb_id: int | None = None

    @field_validator("item_id")
    @classmethod
    def normalize_item_id(cls, value: str) -> str:
        return normalize_jellyfin_item_id(value)

    @model_validator(mode="after")
    def validate_episode_coordinates(self) -> "JellyfinWebhookPayload":
        if self.item_type == "Episode" and (
            self.season_number is None or self.episode_number is None
        ):
            raise ValueError("Episode events require season and episode numbers")
        return self


class JellyfinWebhookIngestRead(KlugBaseModel):
    action: Literal[
        "recorded_only",
        "watch_event_created",
        "duplicate_watch_event_skipped",
        "duplicate_event_ignored",
    ]
    reason: str | None = None
    playback_event: PlaybackEventRead
    watch_event: WatchEventRead | None = None


class JellyfinReconcileRequest(KlugBaseModel):
    klug_user_id: UUID
    since: AwareDatetime | None = None
    dry_run: bool = True
    notes: str | None = None


class JellyfinReconcileIssue(KlugBaseModel):
    item_id: str
    title: str
    reason: str
    play_count: int = 0
    last_played_at: datetime | None = None


class JellyfinReconcileRead(KlugBaseModel):
    import_batch_id: UUID
    status: str
    dry_run: bool
    since: datetime
    cursor_after: datetime
    scanned_count: int
    candidate_count: int
    inserted_count: int
    already_present_count: int
    unmatched_media_count: int
    missing_timestamp_count: int
    ambiguous_play_count: int
    error_count: int
    issue_count: int
    issues: list[JellyfinReconcileIssue]


class JellyfinWatchRestoreRequest(KlugBaseModel):
    klug_user_id: UUID
    dry_run: bool = True
    batch_size: int = Field(default=250, ge=1, le=1000)
    notes: str | None = Field(default=None, max_length=1000)


class JellyfinWatchRestoreIssue(KlugBaseModel):
    item_id: str
    title: str
    reason: str


class JellyfinWatchRestoreRead(KlugBaseModel):
    import_batch_id: UUID
    status: str
    dry_run: bool
    eligible_count: int
    already_played_count: int
    candidate_count: int
    attempted_count: int
    restored_count: int
    remaining_count: int
    movie_candidate_count: int
    episode_candidate_count: int
    error_count: int
    issues: list[JellyfinWatchRestoreIssue]


def ticks_to_seconds(ticks: int | None) -> int | None:
    return ticks // 10_000_000 if ticks is not None else None


def ticks_to_progress_percent(
    position_ticks: int | None,
    runtime_ticks: int | None,
) -> Decimal | None:
    if position_ticks is None or runtime_ticks is None or runtime_ticks <= 0:
        return None
    bounded_position = min(position_ticks, runtime_ticks)
    return (
        Decimal(bounded_position) * Decimal("100") / Decimal(runtime_ticks)
    ).quantize(Decimal("0.01"))
