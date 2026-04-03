from sqlalchemy.orm import Session

from app.repositories import library as library_repository


class LibraryService:
    @staticmethod
    def list_movies(
        session: Session,
        *,
        query: str | None,
        watched: bool | None,
        enrichment_status: str | None,
        year: int | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        return library_repository.list_library_movies(
            session,
            query=query,
            watched=watched,
            enrichment_status=enrichment_status,
            year=year,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def list_episodes(
        session: Session,
        *,
        query: str | None,
        show_query: str | None,
        watched: bool | None,
        enrichment_status: str | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        return library_repository.list_library_episodes(
            session,
            query=query,
            show_query=show_query,
            watched=watched,
            enrichment_status=enrichment_status,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def list_shows(
        session: Session,
        *,
        query: str | None,
        watched: bool | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        return library_repository.list_library_shows(
            session,
            query=query,
            watched=watched,
            limit=limit,
            offset=offset,
        )
