from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.entities import Show
from app.repositories import shows as show_repository


class ShowService:
    @staticmethod
    def find_show_by_tmdb_id(session: Session, *, tmdb_id: int) -> Show | None:
        return show_repository.find_show_by_tmdb_id(session, tmdb_id=tmdb_id)

    @staticmethod
    def get_or_create_show(
        session: Session,
        *,
        tmdb_id: int,
        title: str,
        year: int | None,
        tvdb_id: int | None,
        imdb_id: str | None,
    ) -> Show:
        normalized_title = title.strip()
        normalized_imdb_id = imdb_id.strip() if imdb_id else None
        if not normalized_title:
            raise ValueError("Show title must not be empty")

        existing = show_repository.find_show_by_tmdb_id(session, tmdb_id=tmdb_id)
        if existing is not None:
            return existing

        try:
            with session.begin_nested():
                return show_repository.create_show(
                    session,
                    tmdb_id=tmdb_id,
                    title=normalized_title,
                    year=year,
                    tvdb_id=tvdb_id,
                    imdb_id=normalized_imdb_id,
                )
        except IntegrityError:
            found = show_repository.find_show_by_external_ids(
                session,
                tmdb_id=tmdb_id,
                tvdb_id=tvdb_id,
                imdb_id=normalized_imdb_id,
            )
            if found is None:
                raise
            return found
