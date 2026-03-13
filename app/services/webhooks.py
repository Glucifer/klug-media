from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.entities import WatchEvent
from app.schemas.webhooks import KodiScrobblePayload
from app.services.media_items import MediaItemService
from app.services.shows import ShowService
from app.services.watch_events import WatchEventService


class WebhookService:
    @staticmethod
    def process_kodi_scrobble(
        session: Session,
        *,
        user_id: UUID,
        payload: KodiScrobblePayload,
    ) -> WatchEvent:
        media_item_id: UUID | None = None

        if payload.media_type == "movie":
            # 1. Try to find the movie first by external IDs
            if payload.tmdb_id or payload.imdb_id:
                existing = MediaItemService.find_media_item_by_external_ids(
                    session,
                    media_type="movie",
                    tmdb_id=payload.tmdb_id,
                    imdb_id=payload.imdb_id,
                )
                if existing:
                    media_item_id = existing.media_item_id

            # 2. If not found, create a new media item
            if not media_item_id:
                new_item = MediaItemService.create_media_item(
                    session,
                    media_type="movie",
                    title=payload.title,
                    year=payload.year,
                    tmdb_id=payload.tmdb_id,
                    imdb_id=payload.imdb_id,
                    tvdb_id=payload.tvdb_id,
                )
                media_item_id = new_item.media_item_id
        else:
            # Episode processing
            if not payload.tmdb_id and not payload.tvdb_id and not payload.title:
                raise ValueError("Episode scrobble requires show title or tmdb_id/tvdb_id")
            
            # Since Klug Media tracks episodes by linking to Shows, we first need to ensure the Show exists.
            # Node-Red payload "title" for episodes might be the Show Title! So we will safely use it.
            # Right now, the get_or_create_show expects tmdb_id as mandatory, so we will need to default 
            # if we only have a TVDB ID or TITLE. To keep it robust, let's assume Kodi usually has a TMDB ID 
            # for shows, or we enforce creating a generic show.
            
            # Note: since get_or_create_show requires tmdb_id, let's strictly require it here as per current schema,
            # or fallback to a dummy 0 if title is present (since we need it).
            if not payload.tmdb_id and payload.title:
                # If Kodi only passed title, we can't cleanly use `get_or_create_show` without TMDB id right now
                # without modifying ShowService. Let's raise an explicit error for now so we know if Kodi passes no IDs.
                if not payload.tmdb_id:
                    raise ValueError("Episode scrobble currently requires a tmdb_id to map to a Show.")

            ShowService.get_or_create_show(
                session,
                tmdb_id=payload.tmdb_id, # type: ignore
                title=payload.title,
                year=payload.year,
                tvdb_id=payload.tvdb_id,
                imdb_id=payload.imdb_id,
            )

            # We need an episode MediaItem. Let's create one.
            # In Klug Media, episodes are created as MediaItems then linked.
            # We don't have an episode creation helper in `ShowService` yet, so we will create the media item.
            # For episodes, `imdb_id` corresponds to the episode's IMDB if Kodi provides it, otherwise none
            # Since we don't have a direct "create_episode" service function right now, let's just create a generic
            # episode media item. We really need the endpoint to link it properly, but we will do our best with just MediaItem for watch events.
            new_item = MediaItemService.create_media_item(
                session,
                media_type="episode",
                title=f"{payload.title} - S{payload.season:02d}E{payload.episode:02d}",
                year=payload.year,
                tmdb_id=None, # Kodi probably gave the show's tmdb_id in the payload, not the episode's. Let's leave episode empty.
                imdb_id=None,
                tvdb_id=None,
            )
            media_item_id = new_item.media_item_id

        # 3. Create the watch event
        watch_event = WatchEventService.create_watch_event(
            session,
            user_id=user_id,
            media_item_id=media_item_id, # type: ignore
            watched_at=datetime.now(UTC),
            playback_source=payload.playback_source,
            total_seconds=None,
            watched_seconds=None,
            progress_percent=payload.progress_percent,
            completed=True,
            rating_value=None,
            rating_scale=None,
            media_version_id=None,
            source_event_id=None,
        )

        return watch_event
