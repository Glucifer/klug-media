from sqlalchemy.orm import Session

from app.repositories import collection as collection_repository


class CollectionService:
    @staticmethod
    def list_movies(
        session: Session,
        *,
        query: str | None,
        present: bool | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        return collection_repository.list_collection_movies(
            session,
            query=query,
            present=present,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def list_shows(
        session: Session,
        *,
        query: str | None,
        present: bool | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        return collection_repository.list_collection_shows(
            session,
            query=query,
            present=present,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def list_episodes(
        session: Session,
        *,
        query: str | None,
        present: bool | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        return collection_repository.list_collection_episodes(
            session,
            query=query,
            present=present,
            limit=limit,
            offset=offset,
        )
