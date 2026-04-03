from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.library import LibraryEpisodeRead, LibraryMovieRead, LibraryShowRead
from app.services.library import LibraryService

router = APIRouter(
    prefix="/library",
    tags=["library"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("/movies", response_model=list[LibraryMovieRead])
def list_library_movies(
    query: str | None = Query(default=None, min_length=1, max_length=200),
    watched: bool | None = Query(default=None),
    enrichment_status: str | None = Query(default=None, max_length=40),
    year: int | None = Query(default=None, ge=1800, le=9999),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[LibraryMovieRead]:
    rows = LibraryService.list_movies(
        session,
        query=query,
        watched=watched,
        enrichment_status=enrichment_status,
        year=year,
        limit=limit,
        offset=offset,
    )
    return [LibraryMovieRead.model_validate(row) for row in rows]


@router.get("/episodes", response_model=list[LibraryEpisodeRead])
def list_library_episodes(
    query: str | None = Query(default=None, min_length=1, max_length=200),
    show_query: str | None = Query(default=None, min_length=1, max_length=200),
    watched: bool | None = Query(default=None),
    enrichment_status: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[LibraryEpisodeRead]:
    rows = LibraryService.list_episodes(
        session,
        query=query,
        show_query=show_query,
        watched=watched,
        enrichment_status=enrichment_status,
        limit=limit,
        offset=offset,
    )
    return [LibraryEpisodeRead.model_validate(row) for row in rows]


@router.get("/shows", response_model=list[LibraryShowRead])
def list_library_shows(
    query: str | None = Query(default=None, min_length=1, max_length=200),
    watched: bool | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db_session),
) -> list[LibraryShowRead]:
    rows = LibraryService.list_shows(
        session,
        query=query,
        watched=watched,
        limit=limit,
        offset=offset,
    )
    return [LibraryShowRead.model_validate(row) for row in rows]
