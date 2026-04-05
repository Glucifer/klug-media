import csv
import io
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.horrorfest import (
    HorrorfestAnalyticsComparisonRead,
    HorrorfestAnalyticsCurationReportRead,
    HorrorfestAnalyticsDecadeMatrixRead,
    HorrorfestAnalyticsHighestRatedLeaderboardRead,
    HorrorfestAnalyticsRewatchLeaderboardRead,
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

def _csv_response(
    rows: list[dict[str, object]],
    *,
    fieldnames: list[str],
    filename: str,
) -> Response:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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


@router.get("/analytics/compare", response_model=HorrorfestAnalyticsComparisonRead)
def get_horrorfest_analytics_comparison(
    left_year: int = Query(),
    right_year: int = Query(),
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsComparisonRead:
    try:
        payload = HorrorfestService.get_analytics_comparison(
            session,
            left_year=left_year,
            right_year=right_year,
            user_id=user_id,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in detail.lower()
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=detail) from exc
    return HorrorfestAnalyticsComparisonRead.model_validate(payload)


@router.get(
    "/analytics/leaderboards/repeated-titles",
    response_model=HorrorfestAnalyticsTitleMatrixRead,
)
def get_horrorfest_analytics_repeated_titles_leaderboard(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsTitleMatrixRead:
    return HorrorfestAnalyticsTitleMatrixRead.model_validate(
        HorrorfestService.get_analytics_repeated_titles(session, user_id=user_id)
    )


@router.get(
    "/analytics/leaderboards/highest-rated",
    response_model=HorrorfestAnalyticsHighestRatedLeaderboardRead,
)
def get_horrorfest_analytics_highest_rated_leaderboard(
    user_id: UUID | None = Query(default=None),
    minimum_repeat_count: int = Query(default=2, ge=2),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsHighestRatedLeaderboardRead:
    return HorrorfestAnalyticsHighestRatedLeaderboardRead.model_validate(
        {
            "rows": HorrorfestService.get_analytics_highest_rated_titles(
                session,
                user_id=user_id,
                minimum_repeat_count=minimum_repeat_count,
            )
        }
    )


@router.get(
    "/analytics/leaderboards/rewatches",
    response_model=HorrorfestAnalyticsRewatchLeaderboardRead,
)
def get_horrorfest_analytics_rewatch_leaderboard(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsRewatchLeaderboardRead:
    return HorrorfestAnalyticsRewatchLeaderboardRead.model_validate(
        {
            "rows": HorrorfestService.get_analytics_rewatch_leaderboard(
                session,
                user_id=user_id,
            )
        }
    )


@router.get(
    "/analytics/curation/staples",
    response_model=HorrorfestAnalyticsCurationReportRead,
)
def get_horrorfest_analytics_curation_staples(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsCurationReportRead:
    return HorrorfestAnalyticsCurationReportRead.model_validate(
        {"rows": HorrorfestService.get_analytics_curation_staples(session, user_id=user_id)}
    )


@router.get(
    "/analytics/curation/streaks",
    response_model=HorrorfestAnalyticsCurationReportRead,
)
def get_horrorfest_analytics_curation_streaks(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsCurationReportRead:
    return HorrorfestAnalyticsCurationReportRead.model_validate(
        {"rows": HorrorfestService.get_analytics_curation_streaks(session, user_id=user_id)}
    )


@router.get(
    "/analytics/curation/gaps",
    response_model=HorrorfestAnalyticsCurationReportRead,
)
def get_horrorfest_analytics_curation_gaps(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsCurationReportRead:
    return HorrorfestAnalyticsCurationReportRead.model_validate(
        {"rows": HorrorfestService.get_analytics_curation_gaps(session, user_id=user_id)}
    )


@router.get(
    "/analytics/curation/dormant",
    response_model=HorrorfestAnalyticsCurationReportRead,
)
def get_horrorfest_analytics_curation_dormant(
    user_id: UUID | None = Query(default=None),
    dormant_year_window: int = Query(default=3, ge=1),
    session: Session = Depends(get_db_session),
) -> HorrorfestAnalyticsCurationReportRead:
    return HorrorfestAnalyticsCurationReportRead.model_validate(
        {
            "rows": HorrorfestService.get_analytics_curation_dormant(
                session,
                user_id=user_id,
                dormant_year_window=dormant_year_window,
            )
        }
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


@router.get("/analytics/export/years")
def export_horrorfest_analytics_years(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    rows = HorrorfestService.list_analytics_years(session, user_id=user_id)
    export_rows = [
        {
            "horrorfest_year": row["horrorfest_year"],
            "watch_count": row["watch_count"],
            "watch_days": row["watch_days"],
            "new_watch_count": row["new_watch_count"],
            "rewatch_count": row["rewatch_count"],
            "total_runtime_hours": row["total_runtime_hours"],
            "average_watches_per_day": row["average_watches_per_day"],
            "average_runtime_hours_per_day": row["average_runtime_hours_per_day"],
            "average_runtime_minutes_per_watch": row["average_runtime_minutes_per_watch"],
            "average_rating_value": row["average_rating_value"],
            "first_watch_at": row["first_watch_at"],
            "latest_watch_at": row["latest_watch_at"],
        }
        for row in rows
    ]
    return _csv_response(
        export_rows,
        fieldnames=[
            "horrorfest_year",
            "watch_count",
            "watch_days",
            "new_watch_count",
            "rewatch_count",
            "total_runtime_hours",
            "average_watches_per_day",
            "average_runtime_hours_per_day",
            "average_runtime_minutes_per_watch",
            "average_rating_value",
            "first_watch_at",
            "latest_watch_at",
        ],
        filename="horrorfest_year_summary.csv",
    )


@router.get("/analytics/export/years/{horrorfest_year}/daily")
def export_horrorfest_analytics_year_daily(
    horrorfest_year: int,
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    try:
        detail = HorrorfestService.get_analytics_year_detail(
            session,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _csv_response(
        detail["daily_rows"],
        fieldnames=[
            "watch_date",
            "watch_count",
            "total_runtime_seconds",
            "total_runtime_hours",
            "average_rating_value",
        ],
        filename=f"horrorfest_{horrorfest_year}_daily_activity.csv",
    )


@router.get("/analytics/export/years/{horrorfest_year}/sources")
def export_horrorfest_analytics_year_sources(
    horrorfest_year: int,
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    try:
        detail = HorrorfestService.get_analytics_year_detail(
            session,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _csv_response(
        detail["source_rows"],
        fieldnames=[
            "playback_source",
            "watch_count",
            "total_runtime_seconds",
            "total_runtime_hours",
            "average_rating_value",
        ],
        filename=f"horrorfest_{horrorfest_year}_playback_sources.csv",
    )


@router.get("/analytics/export/years/{horrorfest_year}/ratings")
def export_horrorfest_analytics_year_ratings(
    horrorfest_year: int,
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    try:
        detail = HorrorfestService.get_analytics_year_detail(
            session,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _csv_response(
        detail["rating_rows"],
        fieldnames=["rating_value", "watch_count"],
        filename=f"horrorfest_{horrorfest_year}_rating_distribution.csv",
    )


@router.get("/analytics/export/titles")
def export_horrorfest_title_matrix(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    payload = HorrorfestService.get_analytics_title_matrix(session, user_id=user_id)
    years = payload["years"]
    fieldnames = ["title", "total_count", *[str(year) for year in years]]
    rows = [
        {
            "title": row["title"],
            "total_count": row["total_count"],
            **{str(year): row["year_counts"].get(str(year), 0) for year in years},
        }
        for row in payload["rows"]
    ]
    return _csv_response(rows, fieldnames=fieldnames, filename="horrorfest_title_matrix.csv")


@router.get("/analytics/export/decades")
def export_horrorfest_decade_matrix(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    payload = HorrorfestService.get_analytics_decade_matrix(session, user_id=user_id)
    years = payload["years"]
    fieldnames = ["decade", "total_count", *[str(year) for year in years]]
    rows = [
        {
            "decade": row["decade"],
            "total_count": row["total_count"],
            **{str(year): row["year_counts"].get(str(year), 0) for year in years},
        }
        for row in payload["rows"]
    ]
    return _csv_response(rows, fieldnames=fieldnames, filename="horrorfest_decade_matrix.csv")


@router.get("/analytics/export/compare")
def export_horrorfest_comparison(
    left_year: int = Query(),
    right_year: int = Query(),
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    try:
        payload = HorrorfestService.get_analytics_comparison(
            session,
            left_year=left_year,
            right_year=right_year,
            user_id=user_id,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in detail.lower()
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=detail) from exc
    rows = [
        {
            "section": "summary",
            "metric": "watch_count",
            "left_year": payload["left_summary"]["watch_count"],
            "right_year": payload["right_summary"]["watch_count"],
            "delta": payload["delta"]["watch_count"],
        },
        {
            "section": "summary",
            "metric": "watch_days",
            "left_year": payload["left_summary"]["watch_days"],
            "right_year": payload["right_summary"]["watch_days"],
            "delta": payload["delta"]["watch_days"],
        },
        {
            "section": "summary",
            "metric": "new_watch_count",
            "left_year": payload["left_summary"]["new_watch_count"],
            "right_year": payload["right_summary"]["new_watch_count"],
            "delta": payload["delta"]["new_watch_count"],
        },
        {
            "section": "summary",
            "metric": "rewatch_count",
            "left_year": payload["left_summary"]["rewatch_count"],
            "right_year": payload["right_summary"]["rewatch_count"],
            "delta": payload["delta"]["rewatch_count"],
        },
        {
            "section": "summary",
            "metric": "total_runtime_hours",
            "left_year": payload["left_summary"]["total_runtime_hours"],
            "right_year": payload["right_summary"]["total_runtime_hours"],
            "delta": payload["delta"]["total_runtime_hours"],
        },
        {
            "section": "summary",
            "metric": "average_rating_value",
            "left_year": payload["left_summary"]["average_rating_value"],
            "right_year": payload["right_summary"]["average_rating_value"],
            "delta": payload["delta"]["average_rating_value"],
        },
    ]
    rows.extend(
        {
            "section": "sources",
            "metric": row["playback_source"],
            "left_year": row["left_watch_count"],
            "right_year": row["right_watch_count"],
            "delta": row["delta_watch_count"],
        }
        for row in payload["source_rows"]
    )
    rows.extend(
        {
            "section": "ratings",
            "metric": row["rating_value"],
            "left_year": row["left_watch_count"],
            "right_year": row["right_watch_count"],
            "delta": row["delta_watch_count"],
        }
        for row in payload["rating_rows"]
    )
    rows.extend(
        {
            "section": "repeated_titles",
            "metric": row["title"],
            "left_year": row["left_year_count"],
            "right_year": row["right_year_count"],
            "delta": row["delta_count"],
        }
        for row in payload["repeated_title_rows"]
    )
    return _csv_response(
        rows,
        fieldnames=["section", "metric", "left_year", "right_year", "delta"],
        filename=f"horrorfest_compare_{left_year}_vs_{right_year}.csv",
    )


@router.get("/analytics/export/drilldown")
def export_horrorfest_drilldown(
    kind: str = Query(),
    media_item_id: UUID | None = Query(default=None),
    decade_start: int | None = Query(default=None),
    horrorfest_year: int | None = Query(default=None),
    watch_date: date | None = Query(default=None),
    playback_source: str | None = Query(default=None),
    rating_value: Decimal | None = Query(default=None, ge=0),
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    try:
        if kind == "title" and media_item_id is not None:
            rows = HorrorfestService.list_analytics_title_entries(
                session,
                media_item_id=media_item_id,
                horrorfest_year=horrorfest_year,
                user_id=user_id,
            )
        elif kind == "decade" and decade_start is not None:
            rows = HorrorfestService.list_analytics_decade_entries(
                session,
                decade_start=decade_start,
                horrorfest_year=horrorfest_year,
                user_id=user_id,
            )
        elif kind == "year" and horrorfest_year is not None:
            rows = HorrorfestService.list_analytics_year_entries(
                session,
                horrorfest_year=horrorfest_year,
                watch_date=watch_date,
                playback_source=playback_source,
                rating_value=rating_value,
                user_id=user_id,
            )
        else:
            raise ValueError("Unsupported drilldown export target")
    except ValueError as exc:
        detail = str(exc)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in detail.lower()
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=detail) from exc
    export_rows = [
        {
            "display_title": row["display_title"],
            "horrorfest_year": row["horrorfest_year"],
            "watch_order": row["watch_order"],
            "watched_at": row["watched_at"],
            "effective_runtime_seconds": row["effective_runtime_seconds"],
            "rating_value": row["rating_value"],
            "rewatch": row["rewatch"],
            "playback_source": row["playback_source"],
            "media_item_id": row["media_item_id"],
            "watch_id": row["watch_id"],
        }
        for row in rows
    ]
    return _csv_response(
        export_rows,
        fieldnames=[
            "display_title",
            "horrorfest_year",
            "watch_order",
            "watched_at",
            "effective_runtime_seconds",
            "rating_value",
            "rewatch",
            "playback_source",
            "media_item_id",
            "watch_id",
        ],
        filename="horrorfest_drilldown.csv",
    )


@router.get("/analytics/export/leaderboards/repeated-titles")
def export_horrorfest_repeated_titles_leaderboard(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    payload = HorrorfestService.get_analytics_repeated_titles(session, user_id=user_id)
    years = payload["years"]
    rows = [
        {
            "title": row["title"],
            "total_count": row["total_count"],
            **{str(year): row["year_counts"].get(str(year), 0) for year in years},
        }
        for row in payload["rows"]
    ]
    return _csv_response(
        rows,
        fieldnames=["title", "total_count", *[str(year) for year in years]],
        filename="horrorfest_repeated_titles.csv",
    )


@router.get("/analytics/export/leaderboards/highest-rated")
def export_horrorfest_highest_rated_leaderboard(
    user_id: UUID | None = Query(default=None),
    minimum_repeat_count: int = Query(default=2, ge=2),
    session: Session = Depends(get_db_session),
) -> Response:
    rows = HorrorfestService.get_analytics_highest_rated_titles(
        session,
        user_id=user_id,
        minimum_repeat_count=minimum_repeat_count,
    )
    return _csv_response(
        rows,
        fieldnames=["title", "total_count", "average_rating_value", "rated_watch_count"],
        filename="horrorfest_highest_rated_titles.csv",
    )


@router.get("/analytics/export/leaderboards/rewatches")
def export_horrorfest_rewatch_leaderboard(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    rows = HorrorfestService.get_analytics_rewatch_leaderboard(
        session,
        user_id=user_id,
    )
    return _csv_response(
        rows,
        fieldnames=["title", "total_count", "rewatch_count", "new_watch_count"],
        filename="horrorfest_rewatch_titles.csv",
    )


@router.get("/analytics/export/curation/staples")
def export_horrorfest_curation_staples(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    rows = HorrorfestService.get_analytics_curation_staples(session, user_id=user_id)
    return _csv_response(
        rows,
        fieldnames=[
            "title",
            "total_count",
            "years_seen",
            "first_year",
            "latest_year",
            "current_streak_length",
            "longest_streak_length",
        ],
        filename="horrorfest_annual_staples.csv",
    )


@router.get("/analytics/export/curation/streaks")
def export_horrorfest_curation_streaks(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    rows = HorrorfestService.get_analytics_curation_streaks(session, user_id=user_id)
    return _csv_response(
        rows,
        fieldnames=[
            "title",
            "total_count",
            "years_seen",
            "longest_streak_length",
            "streak_start_year",
            "streak_end_year",
            "current_streak_length",
        ],
        filename="horrorfest_streaks.csv",
    )


@router.get("/analytics/export/curation/gaps")
def export_horrorfest_curation_gaps(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Response:
    rows = HorrorfestService.get_analytics_curation_gaps(session, user_id=user_id)
    return _csv_response(
        rows,
        fieldnames=[
            "title",
            "total_count",
            "years_seen",
            "gap_years",
            "gap_start_year",
            "gap_end_year",
            "latest_year",
        ],
        filename="horrorfest_gaps.csv",
    )


@router.get("/analytics/export/curation/dormant")
def export_horrorfest_curation_dormant(
    user_id: UUID | None = Query(default=None),
    dormant_year_window: int = Query(default=3, ge=1),
    session: Session = Depends(get_db_session),
) -> Response:
    rows = HorrorfestService.get_analytics_curation_dormant(
        session,
        user_id=user_id,
        dormant_year_window=dormant_year_window,
    )
    return _csv_response(
        rows,
        fieldnames=[
            "title",
            "total_count",
            "years_seen",
            "latest_year",
            "years_since_last_seen",
            "current_streak_length",
        ],
        filename="horrorfest_dormant_titles.csv",
    )


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
