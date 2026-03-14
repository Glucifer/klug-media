from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.entities import PlaybackEvent
from app.db.models.entities import WatchEvent
from app.services.playback_events import PlaybackEventService
from app.schemas.webhooks import KodiScrobblePayload
from app.schemas.webhooks import KodiPlaybackEventPayload
from app.services.media_items import MediaItemService
from app.services.shows import ShowService
from app.services.watch_events import WatchEventService


@dataclass
class PlaybackIngestResult:
    action: str
    playback_event: PlaybackEvent
    watch_event: WatchEvent | None = None
    reason: str | None = None


class WebhookService:
    @staticmethod
    def ingest_kodi_playback_event(
        session: Session,
        *,
        payload: KodiPlaybackEventPayload,
    ) -> PlaybackIngestResult:
        playback_event = PlaybackEventService.record_playback_event(
            session,
            collector="node_red",
            playback_source=payload.playback_source,
            event_type=payload.event_type,
            user_id=payload.user_id,
            occurred_at=payload.occurred_at,
            source_event_id=payload.source_event_id,
            session_key=payload.session_key,
            media_type=payload.media_type,
            title=payload.title,
            year=payload.year,
            season_number=payload.season,
            episode_number=payload.episode,
            tmdb_id=payload.tmdb_id,
            imdb_id=payload.imdb_id,
            tvdb_id=payload.tvdb_id,
            progress_percent=payload.progress_percent,
            payload=payload.payload,
        )

        should_create_watch_event = WebhookService._should_create_watch_event(payload)
        if not should_create_watch_event:
            should_create_watch_event = WebhookService._should_create_watch_event_from_session(
                session,
                payload=payload,
            )
        if not should_create_watch_event:
            playback_event = PlaybackEventService.update_playback_event_decision(
                session,
                playback_event=playback_event,
                decision_status="recorded_only",
                decision_reason="Event recorded for later scrobble evaluation",
                watch_id=None,
            )
            return PlaybackIngestResult(
                action="recorded_only",
                playback_event=playback_event,
                reason="Event recorded for later scrobble evaluation",
            )

        if payload.source_event_id and WatchEventService.source_event_exists(
            session,
            playback_source=payload.playback_source,
            source_event_id=payload.source_event_id,
        ):
            playback_event = PlaybackEventService.update_playback_event_decision(
                session,
                playback_event=playback_event,
                decision_status="duplicate_watch_event_skipped",
                decision_reason="Watch event already exists for this source event",
                watch_id=None,
            )
            return PlaybackIngestResult(
                action="duplicate_watch_event_skipped",
                playback_event=playback_event,
                reason="Watch event already exists for this source event",
            )

        if payload.session_key and PlaybackEventService.session_has_prior_scrobble_candidate(
            session,
            collector="node_red",
            playback_source=payload.playback_source,
            user_id=payload.user_id,
            session_key=payload.session_key,
            exclude_playback_event_id=playback_event.playback_event_id,
        ):
            playback_event = PlaybackEventService.update_playback_event_decision(
                session,
                playback_event=playback_event,
                decision_status="duplicate_watch_event_skipped",
                decision_reason="Playback session already produced a watch event",
                watch_id=None,
            )
            return PlaybackIngestResult(
                action="duplicate_watch_event_skipped",
                playback_event=playback_event,
                reason="Playback session already produced a watch event",
            )

        media_item_id = WebhookService._resolve_media_item_id(session, payload=payload)
        watch_event = WatchEventService.create_watch_event(
            session,
            user_id=payload.user_id,
            media_item_id=media_item_id,
            watched_at=payload.occurred_at,
            playback_source=payload.playback_source,
            total_seconds=None,
            watched_seconds=None,
            progress_percent=payload.progress_percent,
            completed=WebhookService._is_completed(payload),
            rating_value=None,
            rating_scale=None,
            media_version_id=None,
            source_event_id=payload.source_event_id,
        )
        playback_event = PlaybackEventService.update_playback_event_decision(
            session,
            playback_event=playback_event,
            decision_status="watch_event_created",
            decision_reason=None,
            watch_id=watch_event.watch_id,
        )

        return PlaybackIngestResult(
            action="watch_event_created",
            playback_event=playback_event,
            watch_event=watch_event,
        )

    @staticmethod
    def process_kodi_scrobble(
        session: Session,
        *,
        user_id: UUID,
        payload: KodiScrobblePayload,
    ) -> WatchEvent:
        scrobble_payload = payload.model_copy(
            update={
                "user_id": user_id,
                "event_type": "scrobble",
            }
        )
        result = WebhookService.ingest_kodi_playback_event(
            session,
            payload=scrobble_payload,
        )
        if result.watch_event is None:
            raise ValueError("Kodi scrobble did not create a watch event")
        return result.watch_event

    @staticmethod
    def _should_create_watch_event(payload: KodiPlaybackEventPayload) -> bool:
        if payload.event_type == "scrobble":
            return True
        if payload.event_type != "stop":
            return False
        if payload.progress_percent is None:
            return False
        return payload.progress_percent >= Decimal("90")

    @staticmethod
    def _is_completed(payload: KodiPlaybackEventPayload) -> bool:
        return payload.event_type == "scrobble" or (
            payload.progress_percent is not None
            and payload.progress_percent >= Decimal("90")
        )

    @staticmethod
    def _should_create_watch_event_from_session(
        session: Session,
        *,
        payload: KodiPlaybackEventPayload,
    ) -> bool:
        if payload.event_type != "stop" or not payload.session_key:
            return False

        max_progress = PlaybackEventService.get_session_max_progress_percent(
            session,
            collector="node_red",
            playback_source=payload.playback_source,
            user_id=payload.user_id,
            session_key=payload.session_key,
        )
        if max_progress is None:
            return False
        return Decimal(str(max_progress)) >= Decimal("90")

    @staticmethod
    def _resolve_media_item_id(
        session: Session,
        *,
        payload: KodiPlaybackEventPayload,
    ) -> UUID:
        if payload.media_type == "movie":
            if payload.tmdb_id or payload.imdb_id:
                existing = MediaItemService.find_media_item_by_external_ids(
                    session,
                    media_type="movie",
                    tmdb_id=payload.tmdb_id,
                    imdb_id=payload.imdb_id,
                )
                if existing is not None:
                    return existing.media_item_id

            new_item = MediaItemService.create_media_item(
                session,
                media_type="movie",
                title=payload.title,
                year=payload.year,
                tmdb_id=payload.tmdb_id,
                imdb_id=payload.imdb_id,
                tvdb_id=payload.tvdb_id,
            )
            return new_item.media_item_id

        if payload.season is None or payload.episode is None:
            raise ValueError(
                "Episode playback event requires season and episode numbers"
            )
        if payload.tmdb_id is None:
            raise ValueError(
                "Episode playback event currently requires a tmdb_id to map to a Show."
            )

        existing_episode = MediaItemService.find_episode_media_item(
            session,
            show_tmdb_id=payload.tmdb_id,
            season_number=payload.season,
            episode_number=payload.episode,
        )
        if existing_episode is not None:
            return existing_episode.media_item_id

        show = ShowService.get_or_create_show(
            session,
            tmdb_id=payload.tmdb_id,
            title=payload.title,
            year=payload.year,
            tvdb_id=payload.tvdb_id,
            imdb_id=payload.imdb_id,
        )
        new_item = MediaItemService.create_media_item(
            session,
            media_type="episode",
            title=payload.title,
            year=payload.year,
            tmdb_id=None,
            imdb_id=None,
            tvdb_id=None,
            show_tmdb_id=payload.tmdb_id,
            season_number=payload.season,
            episode_number=payload.episode,
            show_id=show.show_id,
        )
        return new_item.media_item_id
