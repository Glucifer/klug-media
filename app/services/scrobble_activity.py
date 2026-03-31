from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import scrobble_activity as scrobble_activity_repository


class ScrobbleActivityService:
    @staticmethod
    def list_scrobble_activity(
        session: Session,
        *,
        user_id: UUID | None,
        collector: str | None,
        playback_source: str | None,
        decision_status: str | None,
        event_type: str | None,
        media_type: Literal["movie", "show", "episode"] | None,
        occurred_after: datetime | None,
        occurred_before: datetime | None,
        only_unmatched: bool,
        only_with_watch: bool,
        limit: int,
        offset: int,
    ) -> list[dict[str, object]]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        normalized_collector = collector.strip() if collector is not None else None
        normalized_playback_source = (
            playback_source.strip() if playback_source is not None else None
        )
        normalized_decision_status = (
            decision_status.strip() if decision_status is not None else None
        )
        normalized_event_type = event_type.strip() if event_type is not None else None
        normalized_media_type = media_type.strip() if media_type is not None else None

        return scrobble_activity_repository.list_scrobble_activity(
            session,
            user_id=user_id,
            collector=normalized_collector,
            playback_source=normalized_playback_source,
            decision_status=normalized_decision_status,
            event_type=normalized_event_type,
            media_type=normalized_media_type,
            occurred_after=occurred_after,
            occurred_before=occurred_before,
            only_unmatched=only_unmatched,
            only_with_watch=only_with_watch,
            limit=safe_limit,
            offset=safe_offset,
        )
