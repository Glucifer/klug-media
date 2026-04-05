from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.collection import (
    CollectionEpisodeRead,
    CollectionMovieRead,
    CollectionShowRead,
)
from app.services.collection import CollectionService

router = APIRouter(
    prefix="/collection",
    tags=["collection"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("/movies", response_model=list[CollectionMovieRead])
def list_collection_movies(
    query: str | None = Query(default=None, min_length=1, max_length=200),
    present: bool | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[CollectionMovieRead]:
    rows = CollectionService.list_movies(
        session,
        query=query,
        present=present,
        limit=limit,
        offset=offset,
    )
    return [CollectionMovieRead.model_validate(row) for row in rows]


@router.get("/shows", response_model=list[CollectionShowRead])
def list_collection_shows(
    query: str | None = Query(default=None, min_length=1, max_length=200),
    present: bool | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[CollectionShowRead]:
    rows = CollectionService.list_shows(
        session,
        query=query,
        present=present,
        limit=limit,
        offset=offset,
    )
    return [CollectionShowRead.model_validate(row) for row in rows]


@router.get("/episodes", response_model=list[CollectionEpisodeRead])
def list_collection_episodes(
    query: str | None = Query(default=None, min_length=1, max_length=200),
    present: bool | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[CollectionEpisodeRead]:
    rows = CollectionService.list_episodes(
        session,
        query=query,
        present=present,
        limit=limit,
        offset=offset,
    )
    return [CollectionEpisodeRead.model_validate(row) for row in rows]
