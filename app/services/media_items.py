from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
