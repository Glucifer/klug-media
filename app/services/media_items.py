from dataclasses import dataclass
from datetime import UTC, date, datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.models.entities import MediaItem
from app.core.config import get_settings
from app.repositories import media_items as media_item_repository


class MediaItemAlreadyExistsError(Exception):
    """Raised when a unique media reference already exists."""


@dataclass(frozen=True)
class MediaItemEnrichmentState:
    status: str
    error: str | None = None


class MediaItemService:
    @staticmethod
    def list_media_items(session: Session) -> list[MediaItem]:
        return media_item_repository.list_media_items(session)

    @staticmethod
    def create_media_item(
        session: Session,
        *,
        media_type: str,
        title: str,
        year: int | None,
        tmdb_id: int | None,
        imdb_id: str | None,
        tvdb_id: int | None,
        show_tmdb_id: int | None = None,
        season_number: int | None = None,
        episode_number: int | None = None,
        show_id: UUID | None = None,
        metadata_source: str | None = None,
    ) -> MediaItem:
        normalized_title = title.strip()
        normalized_imdb_id = imdb_id.strip() if imdb_id else None

        if not normalized_title:
            raise ValueError("Title must not be empty")

        enrichment_state = MediaItemService.determine_initial_enrichment_state(
            media_type=media_type,
            tmdb_id=tmdb_id,
            imdb_id=normalized_imdb_id,
            tvdb_id=tvdb_id,
            show_tmdb_id=show_tmdb_id,
        )

        try:
            media_item = media_item_repository.create_media_item(
                session,
                media_type=media_type,
                title=normalized_title,
                year=year,
                tmdb_id=tmdb_id,
                imdb_id=normalized_imdb_id,
                tvdb_id=tvdb_id,
                show_tmdb_id=show_tmdb_id,
                season_number=season_number,
                episode_number=episode_number,
                show_id=show_id,
                metadata_source=metadata_source,
                enrichment_status=enrichment_state.status,
                enrichment_error=enrichment_state.error,
            )
            session.commit()
            return media_item
        except IntegrityError as exc:
            session.rollback()
            raise MediaItemAlreadyExistsError("Duplicate media reference") from exc

    @staticmethod
    def find_media_item_by_external_ids(
        session: Session,
        *,
        media_type: str,
        tmdb_id: int | None,
        imdb_id: str | None,
        tvdb_id: int | None = None,
    ) -> MediaItem | None:
        return media_item_repository.find_media_item_by_external_ids(
            session,
            media_type=media_type,
            tmdb_id=tmdb_id,
            imdb_id=imdb_id,
            tvdb_id=tvdb_id,
        )

    @staticmethod
    def find_episode_media_item(
        session: Session,
        *,
        show_tmdb_id: int,
        season_number: int,
        episode_number: int,
    ) -> MediaItem | None:
        return media_item_repository.find_episode_media_item(
            session,
            show_tmdb_id=show_tmdb_id,
            season_number=season_number,
            episode_number=episode_number,
        )

    @staticmethod
    def get_media_item(session: Session, *, media_item_id: UUID) -> MediaItem | None:
        return media_item_repository.get_media_item(session, media_item_id=media_item_id)

    @staticmethod
    def list_media_items_for_enrichment(
        session: Session,
        *,
        enrichment_status: str | None,
        missing_ids_only: bool,
        limit: int,
        offset: int,
    ) -> list[MediaItem]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        return media_item_repository.list_media_items_for_enrichment(
            session,
            enrichment_status=enrichment_status,
            missing_ids_only=missing_ids_only,
            limit=safe_limit,
            offset=safe_offset,
        )

    @staticmethod
    def count_media_items_for_enrichment(
        session: Session,
        *,
        enrichment_status: str | None,
        missing_ids_only: bool,
    ) -> int:
        return media_item_repository.count_media_items_for_enrichment(
            session,
            enrichment_status=enrichment_status,
            missing_ids_only=missing_ids_only,
        )

    @staticmethod
    def update_media_item_metadata(
        session: Session,
        *,
        media_item: MediaItem,
        title: str | None,
        year: int | None,
        summary: str | None,
        poster_url: str | None,
        release_date: date | None,
        tmdb_id: int | None,
        imdb_id: str | None,
        tvdb_id: int | None,
        show_tmdb_id: int | None,
        show_id: UUID | None,
        base_runtime_seconds: int | None,
        metadata_source: str | None,
        enrichment_status: str,
        enrichment_error: str | None,
        ) -> MediaItem:
        now = datetime.now(UTC)
        return media_item_repository.update_media_item(
            session,
            media_item=media_item,
            title=title,
            year=year,
            summary=summary,
            poster_url=poster_url,
            release_date=release_date,
            tmdb_id=tmdb_id,
            imdb_id=imdb_id,
            tvdb_id=tvdb_id,
            show_tmdb_id=show_tmdb_id,
            show_id=show_id,
            base_runtime_seconds=base_runtime_seconds,
            metadata_source=metadata_source,
            metadata_updated_at=now,
            enrichment_status=enrichment_status,
            enrichment_error=enrichment_error,
            enrichment_attempted_at=now,
        )

    @staticmethod
    def record_enrichment_attempt(
        session: Session,
        *,
        media_item: MediaItem,
        enrichment_status: str,
        enrichment_error: str | None,
    ) -> MediaItem:
        return media_item_repository.record_media_item_enrichment_attempt(
            session,
            media_item=media_item,
            enrichment_status=enrichment_status,
            enrichment_error=enrichment_error,
            enrichment_attempted_at=datetime.now(UTC),
        )

    @staticmethod
    def mark_media_item_for_enrichment(
        session: Session,
        *,
        media_item: MediaItem,
    ) -> MediaItem:
        state = MediaItemService.determine_initial_enrichment_state(
            media_type=media_item.type,
            tmdb_id=media_item.tmdb_id,
            imdb_id=media_item.imdb_id,
            tvdb_id=media_item.tvdb_id,
            show_tmdb_id=media_item.show_tmdb_id,
        )
        return media_item_repository.mark_media_item_enrichment(
            session,
            media_item=media_item,
            enrichment_status=state.status,
            enrichment_error=state.error,
        )

    @staticmethod
    def determine_initial_enrichment_state(
        *,
        media_type: str,
        tmdb_id: int | None,
        imdb_id: str | None,
        tvdb_id: int | None,
        show_tmdb_id: int | None,
    ) -> MediaItemEnrichmentState:
        if not get_settings().klug_metadata_enrichment_enabled:
            return MediaItemEnrichmentState(status="skipped", error="enrichment_disabled")

        if media_type == "movie":
            if tmdb_id is not None or imdb_id:
                return MediaItemEnrichmentState(status="pending")
            return MediaItemEnrichmentState(
                status="skipped",
                error="missing_supported_external_id",
            )

        if media_type == "show":
            if tmdb_id is not None or tvdb_id is not None or imdb_id:
                return MediaItemEnrichmentState(status="pending")
            return MediaItemEnrichmentState(
                status="skipped",
                error="missing_supported_external_id",
            )

        if media_type == "episode":
            if show_tmdb_id is not None or tvdb_id is not None or tmdb_id is not None:
                return MediaItemEnrichmentState(status="pending")
            return MediaItemEnrichmentState(
                status="skipped",
                error="missing_supported_external_id",
            )

        return MediaItemEnrichmentState(status="skipped", error="unsupported_media_type")
