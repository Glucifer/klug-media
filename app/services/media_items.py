from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.models.entities import MediaItem
from app.repositories import media_items as media_item_repository


class MediaItemAlreadyExistsError(Exception):
    """Raised when a unique media reference already exists."""


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
    ) -> MediaItem:
        normalized_title = title.strip()
        normalized_imdb_id = imdb_id.strip() if imdb_id else None

        if not normalized_title:
            raise ValueError("Title must not be empty")

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
    ) -> MediaItem | None:
        return media_item_repository.find_media_item_by_external_ids(
            session,
            media_type=media_type,
            tmdb_id=tmdb_id,
            imdb_id=imdb_id,
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
