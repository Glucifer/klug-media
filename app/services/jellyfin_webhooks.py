from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from sqlalchemy.orm import Session

from app.db.models.entities import PlaybackEvent, WatchEvent
from app.repositories import media_items as media_item_repository
from app.repositories import playback_events as playback_event_repository
from app.repositories import watch_events as watch_event_repository
from app.schemas.jellyfin_integration import (
    JellyfinWebhookPayload,
    ticks_to_progress_percent,
    ticks_to_seconds,
)
from app.services.playback_events import (
    PlaybackEventDuplicateError,
    PlaybackEventService,
)
from app.services.users import UserService
from app.services.watch_events import WatchEventService
from app.core.config import get_settings


@dataclass(frozen=True)
class JellyfinWebhookIngestResult:
    action: str
    playback_event: PlaybackEvent
    watch_event: WatchEvent | None = None
    reason: str | None = None


class JellyfinWebhookService:
    COLLECTOR = "jellyfin_webhook"
    PLAYBACK_SOURCE = "jellyfin"

    @staticmethod
    def ingest(
        session: Session,
        *,
        payload: JellyfinWebhookPayload,
    ) -> JellyfinWebhookIngestResult:
        user = UserService.get_user_by_jellyfin_user_id(
            session,
            jellyfin_user_id=payload.jellyfin_user_id,
        )
        if user is None:
            raise ValueError(
                f"Jellyfin user '{payload.jellyfin_user_id}' is not mapped to Klug"
            )

        source_event_id = JellyfinWebhookService._source_event_id(payload)
        progress_percent = ticks_to_progress_percent(
            payload.playback_position_ticks,
            payload.runtime_ticks,
        )
        total_seconds = ticks_to_seconds(payload.runtime_ticks)
        watched_seconds = ticks_to_seconds(payload.playback_position_ticks)
        raw_payload = payload.model_dump(mode="json")

        try:
            playback_event = PlaybackEventService.record_playback_event(
                session,
                collector=JellyfinWebhookService.COLLECTOR,
                playback_source=JellyfinWebhookService.PLAYBACK_SOURCE,
                event_type={
                    "PlaybackStart": "play",
                    "PlaybackStop": "stop",
                }[payload.notification_type],
                user_id=user.user_id,
                occurred_at=payload.occurred_at,
                source_event_id=source_event_id,
                session_key=None,
                media_type={"Movie": "movie", "Episode": "episode"}[payload.item_type],
                title=payload.title,
                year=payload.year,
                season_number=payload.season_number,
                episode_number=payload.episode_number,
                tmdb_id=payload.tmdb_id,
                imdb_id=payload.imdb_id,
                tvdb_id=payload.tvdb_id,
                total_seconds=total_seconds,
                watched_seconds=watched_seconds,
                progress_percent=progress_percent,
                payload=raw_payload,
            )
        except PlaybackEventDuplicateError:
            existing = playback_event_repository.get_playback_event_by_source_event_id(
                session,
                collector=JellyfinWebhookService.COLLECTOR,
                source_event_id=source_event_id,
            )
            if existing is None:
                raise
            watch_event = (
                watch_event_repository.get_watch_event(
                    session, watch_id=existing.watch_id
                )
                if existing.watch_id is not None
                else None
            )
            return JellyfinWebhookIngestResult(
                action="duplicate_event_ignored",
                playback_event=existing,
                watch_event=watch_event,
                reason="Webhook event was already processed",
            )

        if payload.notification_type == "PlaybackStart":
            return JellyfinWebhookService._record_only(
                session,
                playback_event=playback_event,
                reason="Playback start recorded for evidence",
            )

        completed = payload.played_to_completion or (
            progress_percent is not None
            and progress_percent >= get_settings().klug_scrobble_min_progress_percent
        )
        if not completed:
            return JellyfinWebhookService._record_only(
                session,
                playback_event=playback_event,
                reason="Playback stop did not meet completion threshold",
            )

        media_item = media_item_repository.find_media_item_by_jellyfin_item_id(
            session,
            jellyfin_item_id=payload.item_id,
        )
        if media_item is None:
            return JellyfinWebhookService._record_only(
                session,
                playback_event=playback_event,
                reason="Jellyfin item is not mapped to a Klug media item",
            )

        watch_result = WatchEventService.create_watch_event(
            session,
            user_id=user.user_id,
            media_item_id=media_item.media_item_id,
            watched_at=payload.occurred_at,
            playback_source=JellyfinWebhookService.PLAYBACK_SOURCE,
            total_seconds=total_seconds,
            watched_seconds=watched_seconds,
            progress_percent=progress_percent,
            completed=True,
            rating_value=None,
            rating_scale=None,
            media_version_id=None,
            source_event_id=source_event_id,
            origin_kind="live_playback",
            origin_playback_event_id=playback_event.playback_event_id,
        )
        action = (
            "watch_event_created"
            if watch_result.created
            else "duplicate_watch_event_skipped"
        )
        reason = None if watch_result.created else "Matched an existing watch event"
        playback_event = PlaybackEventService.update_playback_event_decision(
            session,
            playback_event=playback_event,
            decision_status=action,
            decision_reason=reason,
            watch_id=watch_result.watch_event.watch_id,
        )
        return JellyfinWebhookIngestResult(
            action=action,
            playback_event=playback_event,
            watch_event=watch_result.watch_event,
            reason=reason,
        )

    @staticmethod
    def _record_only(
        session: Session,
        *,
        playback_event: PlaybackEvent,
        reason: str,
    ) -> JellyfinWebhookIngestResult:
        playback_event = PlaybackEventService.update_playback_event_decision(
            session,
            playback_event=playback_event,
            decision_status="recorded_only",
            decision_reason=reason,
            watch_id=None,
        )
        return JellyfinWebhookIngestResult(
            action="recorded_only",
            playback_event=playback_event,
            reason=reason,
        )

    @staticmethod
    def _source_event_id(payload: JellyfinWebhookPayload) -> str:
        identity = "|".join(
            [
                payload.server_id.strip().lower(),
                payload.notification_type,
                payload.jellyfin_user_id.hex,
                payload.item_id,
                (payload.device_id or "").strip().lower(),
                payload.occurred_at.isoformat(),
            ]
        )
        return f"jellyfin:{sha256(identity.encode('utf-8')).hexdigest()}"
