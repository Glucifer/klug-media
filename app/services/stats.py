from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import stats as stats_repository


class StatsService:
    @staticmethod
    def get_summary(
        session: Session,
        *,
        user_id: UUID | None,
    ) -> dict[str, object]:
        return stats_repository.get_summary_stats(session, user_id=user_id)

    @staticmethod
    def list_monthly(
        session: Session,
        *,
        user_id: UUID | None,
    ) -> list[dict[str, object]]:
        return stats_repository.list_monthly_stats(session, user_id=user_id)

    @staticmethod
    def list_horrorfest(
        session: Session,
        *,
        user_id: UUID | None,
    ) -> list[dict[str, object]]:
        return stats_repository.list_horrorfest_stats(session, user_id=user_id)
