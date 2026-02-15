from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.schemas.imports import ImportedWatchEvent


@dataclass(frozen=True)
class WatchEventCreateArgs:
    user_id: UUID
    media_item_id: UUID
    watched_at: datetime
    playback_source: str
    total_seconds: int | None
    watched_seconds: int | None
    progress_percent: Decimal | None
    completed: bool
    rating_value: Decimal | None
    rating_scale: str | None
    media_version_id: UUID | None
    source_event_id: str | None


class WatchEventImportAdapter:
    def to_watch_event_create_args(
        self,
        event: ImportedWatchEvent,
    ) -> WatchEventCreateArgs:
        return WatchEventCreateArgs(
            user_id=event.user_id,
            media_item_id=event.media_item_id,
            watched_at=event.watched_at,
            playback_source=event.playback_source,
            total_seconds=event.total_seconds,
            watched_seconds=event.watched_seconds,
            progress_percent=event.progress_percent,
            completed=event.completed,
            rating_value=event.rating_value,
            rating_scale=event.rating_scale,
            media_version_id=event.media_version_id,
            source_event_id=event.source_event_id,
        )


def get_watch_event_import_adapter(source: str) -> WatchEventImportAdapter:
    normalized_source = source.strip().lower()
    if normalized_source in {"legacy_source_export", "manual_bulk"}:
        return WatchEventImportAdapter()
    raise ValueError(f"Unsupported import source: {source}")
