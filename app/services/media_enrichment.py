from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.entities import MediaItem
from app.services.media_items import MediaItemService
from app.services.shows import ShowService
from app.services.tmdb import TmdbLookupError, TmdbService


@dataclass(frozen=True)
class MediaEnrichmentResult:
    media_item: MediaItem
    action: Literal["enriched", "failed", "skipped"]
    reason: str | None = None


class MediaEnrichmentService:
    @staticmethod
    def list_queue(
        session: Session,
        *,
        enrichment_status: str | None,
        missing_ids_only: bool,
        limit: int,
        offset: int,
    ) -> list[MediaItem]:
        return MediaItemService.list_media_items_for_enrichment(
            session,
            enrichment_status=enrichment_status,
            missing_ids_only=missing_ids_only,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def process_pending_items(
        session: Session,
        *,
        limit: int,
    ) -> list[MediaEnrichmentResult]:
        items = MediaItemService.list_media_items_for_enrichment(
            session,
            enrichment_status="pending",
            missing_ids_only=False,
            limit=limit,
            offset=0,
        )
        return [
            MediaEnrichmentService.enrich_media_item(
                session,
                media_item_id=item.media_item_id,
            )
            for item in items
        ]

    @staticmethod
    def retry_media_item(
        session: Session,
        *,
        media_item_id: UUID,
    ) -> MediaEnrichmentResult:
        return MediaEnrichmentService.enrich_media_item(
            session,
            media_item_id=media_item_id,
        )

    @staticmethod
    def enrich_media_item(
        session: Session,
        *,
        media_item_id: UUID,
    ) -> MediaEnrichmentResult:
        media_item = MediaItemService.get_media_item(session, media_item_id=media_item_id)
        if media_item is None:
            raise ValueError(f"Media item '{media_item_id}' not found")

        if not TmdbService.is_enabled():
            updated = MediaItemService.update_media_item_metadata(
                session,
                media_item=media_item,
                title=media_item.title,
                year=media_item.year,
                summary=media_item.summary,
                poster_url=media_item.poster_url,
                release_date=media_item.release_date,
                tmdb_id=media_item.tmdb_id,
                imdb_id=media_item.imdb_id,
                tvdb_id=media_item.tvdb_id,
                show_tmdb_id=media_item.show_tmdb_id,
                show_id=media_item.show_id,
                base_runtime_seconds=media_item.base_runtime_seconds,
                metadata_source=media_item.metadata_source,
                enrichment_status="skipped",
                enrichment_error="enrichment_disabled_or_unconfigured",
            )
            session.commit()
            return MediaEnrichmentResult(
                media_item=updated,
                action="skipped",
                reason="enrichment_disabled_or_unconfigured",
            )

        try:
            updated = MediaEnrichmentService._enrich_with_tmdb(session, media_item=media_item)
            session.commit()
            return MediaEnrichmentResult(media_item=updated, action="enriched")
        except TmdbLookupError as exc:
            session.rollback()
            media_item = MediaItemService.get_media_item(session, media_item_id=media_item_id)
            assert media_item is not None
            updated = MediaItemService.update_media_item_metadata(
                session,
                media_item=media_item,
                title=media_item.title,
                year=media_item.year,
                summary=media_item.summary,
                poster_url=media_item.poster_url,
                release_date=media_item.release_date,
                tmdb_id=media_item.tmdb_id,
                imdb_id=media_item.imdb_id,
                tvdb_id=media_item.tvdb_id,
                show_tmdb_id=media_item.show_tmdb_id,
                show_id=media_item.show_id,
                base_runtime_seconds=media_item.base_runtime_seconds,
                metadata_source=media_item.metadata_source,
                enrichment_status="failed",
                enrichment_error=str(exc),
            )
            session.commit()
            return MediaEnrichmentResult(
                media_item=updated,
                action="failed",
                reason=str(exc),
            )
        except Exception as exc:
            session.rollback()
            media_item = MediaItemService.get_media_item(session, media_item_id=media_item_id)
            assert media_item is not None
            updated = MediaItemService.update_media_item_metadata(
                session,
                media_item=media_item,
                title=media_item.title,
                year=media_item.year,
                summary=media_item.summary,
                poster_url=media_item.poster_url,
                release_date=media_item.release_date,
                tmdb_id=media_item.tmdb_id,
                imdb_id=media_item.imdb_id,
                tvdb_id=media_item.tvdb_id,
                show_tmdb_id=media_item.show_tmdb_id,
                show_id=media_item.show_id,
                base_runtime_seconds=media_item.base_runtime_seconds,
                metadata_source=media_item.metadata_source,
                enrichment_status="failed",
                enrichment_error=str(exc),
            )
            session.commit()
            return MediaEnrichmentResult(
                media_item=updated,
                action="failed",
                reason=str(exc),
            )

    @staticmethod
    def _enrich_with_tmdb(session: Session, *, media_item: MediaItem) -> MediaItem:
        if media_item.type == "movie":
            return MediaEnrichmentService._enrich_movie(session, media_item=media_item)
        if media_item.type == "show":
            return MediaEnrichmentService._enrich_show(session, media_item=media_item)
        if media_item.type == "episode":
            return MediaEnrichmentService._enrich_episode(session, media_item=media_item)
        raise TmdbLookupError(f"Unsupported media type '{media_item.type}'")

    @staticmethod
    def _enrich_movie(session: Session, *, media_item: MediaItem) -> MediaItem:
        tmdb_id = media_item.tmdb_id
        if tmdb_id is None:
            if not media_item.imdb_id:
                raise TmdbLookupError("missing_supported_external_id")
            match = TmdbService.find_by_external_id(
                session,
                external_id=media_item.imdb_id,
                external_source="imdb_id",
                media_type="movie",
            )
            tmdb_id = match.tmdb_id

        details = TmdbService.get_movie_details(session, tmdb_id=tmdb_id)
        return MediaItemService.update_media_item_metadata(
            session,
            media_item=media_item,
            title=details.get("title") or media_item.title,
            year=MediaEnrichmentService._extract_year(details.get("release_date")) or media_item.year,
            summary=details.get("overview") or None,
            poster_url=MediaEnrichmentService._poster_url(details.get("poster_path")),
            release_date=MediaEnrichmentService._parse_date(details.get("release_date")),
            tmdb_id=tmdb_id,
            imdb_id=media_item.imdb_id,
            tvdb_id=media_item.tvdb_id,
            show_tmdb_id=media_item.show_tmdb_id,
            show_id=media_item.show_id,
            base_runtime_seconds=MediaEnrichmentService._runtime_seconds(details.get("runtime")),
            metadata_source="tmdb",
            enrichment_status="enriched",
            enrichment_error=None,
        )

    @staticmethod
    def _enrich_show(session: Session, *, media_item: MediaItem) -> MediaItem:
        show_tmdb_id = media_item.tmdb_id
        if show_tmdb_id is None:
            if media_item.tvdb_id is not None:
                match = TmdbService.find_by_external_id(
                    session,
                    external_id=media_item.tvdb_id,
                    external_source="tvdb_id",
                    media_type="tv",
                )
                show_tmdb_id = match.tmdb_id
            elif media_item.imdb_id:
                match = TmdbService.find_by_external_id(
                    session,
                    external_id=media_item.imdb_id,
                    external_source="imdb_id",
                    media_type="tv",
                )
                show_tmdb_id = match.tmdb_id
            else:
                raise TmdbLookupError("missing_supported_external_id")

        details = TmdbService.get_tv_details(session, tmdb_id=show_tmdb_id)
        show = ShowService.upsert_show(
            session,
            tmdb_id=show_tmdb_id,
            title=details.get("name") or media_item.title,
            year=MediaEnrichmentService._extract_year(details.get("first_air_date")) or media_item.year,
            tvdb_id=media_item.tvdb_id,
            imdb_id=media_item.imdb_id,
        )
        return MediaItemService.update_media_item_metadata(
            session,
            media_item=media_item,
            title=details.get("name") or media_item.title,
            year=MediaEnrichmentService._extract_year(details.get("first_air_date")) or media_item.year,
            summary=details.get("overview") or None,
            poster_url=MediaEnrichmentService._poster_url(details.get("poster_path")),
            release_date=MediaEnrichmentService._parse_date(details.get("first_air_date")),
            tmdb_id=show_tmdb_id,
            imdb_id=media_item.imdb_id,
            tvdb_id=media_item.tvdb_id,
            show_tmdb_id=media_item.show_tmdb_id,
            show_id=show.show_id,
            base_runtime_seconds=MediaEnrichmentService._runtime_seconds_from_list(details.get("episode_run_time")),
            metadata_source="tmdb",
            enrichment_status="enriched",
            enrichment_error=None,
        )

    @staticmethod
    def _enrich_episode(session: Session, *, media_item: MediaItem) -> MediaItem:
        show_tmdb_id = media_item.show_tmdb_id or media_item.tmdb_id
        if show_tmdb_id is None:
            if media_item.tvdb_id is None:
                raise TmdbLookupError("missing_supported_external_id")
            match = TmdbService.find_by_external_id(
                session,
                external_id=media_item.tvdb_id,
                external_source="tvdb_id",
                media_type="tv",
            )
            show_tmdb_id = match.resolved_show_tmdb_id or match.tmdb_id

        if media_item.season_number is None or media_item.episode_number is None:
            raise TmdbLookupError("missing_season_or_episode_number")

        show_details = TmdbService.get_tv_details(session, tmdb_id=show_tmdb_id)
        episode_details = TmdbService.get_episode_details(
            session,
            show_tmdb_id=show_tmdb_id,
            season_number=media_item.season_number,
            episode_number=media_item.episode_number,
        )
        show = ShowService.upsert_show(
            session,
            tmdb_id=show_tmdb_id,
            title=show_details.get("name") or media_item.title,
            year=MediaEnrichmentService._extract_year(show_details.get("first_air_date")) or media_item.year,
            tvdb_id=media_item.tvdb_id,
            imdb_id=media_item.imdb_id,
        )
        return MediaItemService.update_media_item_metadata(
            session,
            media_item=media_item,
            title=episode_details.get("name") or media_item.title,
            year=MediaEnrichmentService._extract_year(episode_details.get("air_date")) or media_item.year,
            summary=episode_details.get("overview") or None,
            poster_url=MediaEnrichmentService._poster_url(episode_details.get("still_path")),
            release_date=MediaEnrichmentService._parse_date(episode_details.get("air_date")),
            tmdb_id=media_item.tmdb_id,
            imdb_id=media_item.imdb_id,
            tvdb_id=media_item.tvdb_id,
            show_tmdb_id=show_tmdb_id,
            show_id=show.show_id,
            base_runtime_seconds=MediaEnrichmentService._runtime_seconds(episode_details.get("runtime")),
            metadata_source="tmdb",
            enrichment_status="enriched",
            enrichment_error=None,
        )

    @staticmethod
    def _poster_url(path: str | None) -> str | None:
        if not path:
            return None
        return f"https://image.tmdb.org/t/p/w500{path}"

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None

    @staticmethod
    def _extract_year(value: str | None) -> int | None:
        parsed = MediaEnrichmentService._parse_date(value)
        return parsed.year if parsed is not None else None

    @staticmethod
    def _runtime_seconds(value: int | None) -> int | None:
        if value is None:
            return None
        return max(0, value) * 60

    @staticmethod
    def _runtime_seconds_from_list(values: object) -> int | None:
        if not isinstance(values, list) or not values:
            return None
        first = values[0]
        if not isinstance(first, int):
            return None
        return MediaEnrichmentService._runtime_seconds(first)
