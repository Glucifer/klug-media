from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.horrorfest import (
    HorrorfestAnalyticsDecadeMatrixRead,
    HorrorfestAnalyticsTitleMatrixRead,
    HorrorfestAnalyticsYearDetailRead,
    HorrorfestAnalyticsYearRead,
    HorrorfestEntryInclude,
    HorrorfestEntryMove,
    HorrorfestEntryMutation,
    HorrorfestEntryRead,
    HorrorfestYearRead,
    HorrorfestYearUpsert,
)
from app.services.horrorfest import HorrorfestConstraintError, HorrorfestService

router = APIRouter(
    prefix="/horrorfest",
    tags=["horrorfest"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("/years", response_model=list[HorrorfestYearRead])
def list_horrorfest_years(
    session: Session = Depends(get_db_session),
) -> list[HorrorfestYearRead]:
    return [
        HorrorfestYearRead.model_validate(item)
        for item in HorrorfestService.list_years(session)
    ]


@router.get("/analytics/years", response_model=list[HorrorfestAnalyticsYearRead])
def list_horrorfest_analytics_years(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> list[HorrorfestAnalyticsYearRead]:
    return [
        HorrorfestAnalyticsYearRead.model_validate(item)
        for item in HorrorfestService.list_analytics_years(session, user_id=user_id)
    ]


@router.get("/analytics/titles", response_model=HorrorfestAnalyticsTitleMatrixRead)
def get_horrorfest_analytics_title_matrix(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsTitleMatrixRead:
    return HorrorfestAnalyticsTitleMatrixRead.model_validate(
        HorrorfestService.get_analytics_title_matrix(session, user_id=user_id)
    )


@router.get(
    "/analytics/titles/{media_item_id}/entries",
    response_model=list[HorrorfestEntryRead],
)
def list_horrorfest_analytics_title_entries(
    media_item_id: UUID,
    horrorfest_year: int | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> list[HorrorfestEntryRead]:
    return [
        HorrorfestEntryRead.model_validate(item)
        for item in HorrorfestService.list_analytics_title_entries(
            session,
            media_item_id=media_item_id,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )
    ]


@router.get("/analytics/decades", response_model=HorrorfestAnalyticsDecadeMatrixRead)
def get_horrorfest_analytics_decade_matrix(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsDecadeMatrixRead:
    return HorrorfestAnalyticsDecadeMatrixRead.model_validate(
        HorrorfestService.get_analytics_decade_matrix(session, user_id=user_id)
    )


@router.get(
    "/analytics/decades/{decade_start}/entries",
    response_model=list[HorrorfestEntryRead],
)
def list_horrorfest_analytics_decade_entries(
    decade_start: int,
    horrorfest_year: int | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> list[HorrorfestEntryRead]:
    try:
        rows = HorrorfestService.list_analytics_decade_entries(
            session,
            decade_start=decade_start,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return [HorrorfestEntryRead.model_validate(item) for item in rows]


@router.get(
    "/analytics/years/{horrorfest_year}",
    response_model=HorrorfestAnalyticsYearDetailRead,
)
def get_horrorfest_analytics_year_detail(
    horrorfest_year: int,
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsYearDetailRead:
    try:
        detail = HorrorfestService.get_analytics_year_detail(
            session,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return HorrorfestAnalyticsYearDetailRead.model_validate(detail)


@router.get(
    "/analytics/years/{horrorfest_year}/entries",
    response_model=list[HorrorfestEntryRead],
)
def list_horrorfest_analytics_year_entries(
    horrorfest_year: int,
    watch_date: date | None = Query(default=None),
    playback_source: str | None = Query(default=None),
    rating_value: Decimal | None = Query(default=None, ge=0),
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> list[HorrorfestEntryRead]:
    try:
        rows = HorrorfestService.list_analytics_year_entries(
            session,
            horrorfest_year=horrorfest_year,
            watch_date=watch_date,
            playback_source=playback_source,
            rating_value=rating_value,
            user_id=user_id,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return [HorrorfestEntryRead.model_validate(item) for item in rows]


@router.put("/years/{horrorfest_year}", response_model=HorrorfestYearRead)
def upsert_horrorfest_year(
    horrorfest_year: int,
    payload: HorrorfestYearUpsert,
    session: Session = Depends(get_db_session),
) -> HorrorfestYearRead:
    try:
        result = HorrorfestService.upsert_year_config(
            session,
            horrorfest_year=horrorfest_year,
            window_start_at=payload.window_start_at,
            window_end_at=payload.window_end_at,
            label=payload.label,
            notes=payload.notes,
            is_active=payload.is_active,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except HorrorfestConstraintError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    rows = HorrorfestService.list_years(session)
    selected = next(
        item for item in rows if item["horrorfest_year"] == result.horrorfest_year
    )
    return HorrorfestYearRead.model_validate(selected)


@router.get("/years/{horrorfest_year}/entries", response_model=list[HorrorfestEntryRead])
def list_horrorfest_entries(
    horrorfest_year: int,
    include_removed: bool = Query(default=False),
    session: Session = Depends(get_db_session),
) -> list[HorrorfestEntryRead]:
    try:
        rows = HorrorfestService.list_entries(
            session,
            horrorfest_year=horrorfest_year,
            include_removed=include_removed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [HorrorfestEntryRead.model_validate(item) for item in rows]


@router.post("/watch-events/{watch_id}/include", response_model=HorrorfestEntryRead)
def include_watch_event_in_horrorfest(
    watch_id: UUID,
    payload: HorrorfestEntryInclude,
    session: Session = Depends(get_db_session),
) -> HorrorfestEntryRead:
    try:
        HorrorfestService.include_watch_event(
            session,
            watch_id=watch_id,
            horrorfest_year=payload.horrorfest_year,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
            target_order=payload.target_order,
        )
        rows = HorrorfestService.list_entries(
            session,
            horrorfest_year=payload.horrorfest_year,
            include_removed=True,
        )
        selected = next(item for item in rows if item["watch_id"] == watch_id and not item["is_removed"])
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except HorrorfestConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return HorrorfestEntryRead.model_validate(selected)


@router.post("/entries/{horrorfest_entry_id}/remove", response_model=HorrorfestEntryRead)
def remove_horrorfest_entry(
    horrorfest_entry_id: UUID,
    payload: HorrorfestEntryMutation,
    session: Session = Depends(get_db_session),
) -> HorrorfestEntryRead:
    try:
        entry = HorrorfestService.remove_entry(
            session,
            horrorfest_entry_id=horrorfest_entry_id,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except HorrorfestConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    rows = HorrorfestService.list_entries(
        session,
        horrorfest_year=entry.horrorfest_year,
        include_removed=True,
    )
    selected = next(item for item in rows if item["horrorfest_entry_id"] == entry.horrorfest_entry_id)
    return HorrorfestEntryRead.model_validate(selected)


@router.post("/entries/{horrorfest_entry_id}/restore", response_model=HorrorfestEntryRead)
def restore_horrorfest_entry(
    horrorfest_entry_id: UUID,
    payload: HorrorfestEntryMutation,
    session: Session = Depends(get_db_session),
) -> HorrorfestEntryRead:
    try:
        entry = HorrorfestService.restore_entry(
            session,
            horrorfest_entry_id=horrorfest_entry_id,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except HorrorfestConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    rows = HorrorfestService.list_entries(
        session,
        horrorfest_year=entry.horrorfest_year,
        include_removed=True,
    )
    selected = next(item for item in rows if item["horrorfest_entry_id"] == entry.horrorfest_entry_id)
    return HorrorfestEntryRead.model_validate(selected)


@router.post("/entries/{horrorfest_entry_id}/move", response_model=HorrorfestEntryRead)
def move_horrorfest_entry(
    horrorfest_entry_id: UUID,
    payload: HorrorfestEntryMove,
    session: Session = Depends(get_db_session),
) -> HorrorfestEntryRead:
    try:
        entry = HorrorfestService.move_entry(
            session,
            horrorfest_entry_id=horrorfest_entry_id,
            updated_by=payload.updated_by,
            update_reason=payload.update_reason,
            target_order=payload.target_order,
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except HorrorfestConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    rows = HorrorfestService.list_entries(
        session,
        horrorfest_year=entry.horrorfest_year,
        include_removed=True,
    )
    selected = next(item for item in rows if item["horrorfest_entry_id"] == entry.horrorfest_entry_id)
    return HorrorfestEntryRead.model_validate(selected)
