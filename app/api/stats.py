from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.db.session import get_db_session
from app.schemas.stats import StatsHorrorfestRead, StatsMonthlyRead, StatsSummaryRead
from app.services.stats import StatsService

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    dependencies=[Depends(require_request_auth)],
)


@router.get("/summary", response_model=StatsSummaryRead)
def get_stats_summary(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> StatsSummaryRead:
    return StatsSummaryRead.model_validate(
        StatsService.get_summary(session, user_id=user_id)
    )


@router.get("/monthly", response_model=list[StatsMonthlyRead])
def list_monthly_stats(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> list[StatsMonthlyRead]:
    return [
        StatsMonthlyRead.model_validate(item)
        for item in StatsService.list_monthly(session, user_id=user_id)
    ]


@router.get("/horrorfest", response_model=list[StatsHorrorfestRead])
def list_horrorfest_stats(
    user_id: UUID | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> list[StatsHorrorfestRead]:
    return [
        StatsHorrorfestRead.model_validate(item)
        for item in StatsService.list_horrorfest(session, user_id=user_id)
    ]
