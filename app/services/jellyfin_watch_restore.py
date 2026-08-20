from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import media_items as media_item_repository
from app.schemas.jellyfin_integration import (
    JellyfinWatchRestoreIssue,
    JellyfinWatchRestoreRead,
    JellyfinWatchRestoreRequest,
)
from app.services.import_batches import ImportBatchService
from app.services.jellyfin import JellyfinClient, JellyfinPlayedUpdate
from app.services.users import UserService


class JellyfinWatchRestoreService:
    SOURCE = "jellyfin_watch_restore"
    MAX_RETURNED_ISSUES = 100

    @staticmethod
    def run(
        session: Session,
        *,
        payload: JellyfinWatchRestoreRequest,
        client: JellyfinClient | None = None,
    ) -> JellyfinWatchRestoreRead:
        user = UserService.get_user_by_id(session, payload.klug_user_id)
        if user is None:
            raise ValueError(f"User '{payload.klug_user_id}' not found")
        if user.jellyfin_user_id is None:
            raise ValueError("Klug user is not mapped to a Jellyfin user")

        jellyfin_client = client or JellyfinClient.from_settings()
        eligible = media_item_repository.list_present_jellyfin_watched_items(
            session,
            user_id=user.user_id,
        )
        played_ids = {
            item.source_item_id
            for item in jellyfin_client.list_played_items(
                user_id=user.jellyfin_user_id,
            )
            if item.played
        }
        candidates = [item for item in eligible if item["item_id"] not in played_ids]
        movie_candidate_count = sum(
            item["media_type"] == "movie" for item in candidates
        )
        episode_candidate_count = sum(
            item["media_type"] == "episode" for item in candidates
        )

        if payload.dry_run:
            return JellyfinWatchRestoreService._result(
                dry_run=True,
                status="dry_run",
                eligible_count=len(eligible),
                candidate_count=len(candidates),
                attempted_count=0,
                restored_count=0,
                movie_candidate_count=movie_candidate_count,
                episode_candidate_count=episode_candidate_count,
                error_count=0,
                issues=[],
            )

        selected = candidates[: payload.batch_size]
        batch = ImportBatchService.start_import_batch(
            session,
            source=JellyfinWatchRestoreService.SOURCE,
            source_detail=str(user.user_id),
            notes=payload.notes,
            parameters={
                "jellyfin_user_id": str(user.jellyfin_user_id),
                "eligible_count": len(eligible),
                "candidate_count": len(candidates),
                "batch_size": payload.batch_size,
                "dry_run": False,
            },
        )
        updates = [
            JellyfinPlayedUpdate(
                item_id=str(item["item_id"]),
                date_played=item["last_watched_at"],
            )
            for item in selected
        ]
        update_results = jellyfin_client.mark_items_played(
            user_id=user.jellyfin_user_id,
            updates=updates,
        )
        selected_by_id = {str(item["item_id"]): item for item in selected}
        issues: list[JellyfinWatchRestoreIssue] = []
        restored_count = 0
        for update_result in update_results:
            if update_result.succeeded:
                restored_count += 1
                continue
            item = selected_by_id[update_result.item_id]
            issue = JellyfinWatchRestoreIssue(
                item_id=update_result.item_id,
                title=str(item["title"]),
                reason=update_result.error or "Jellyfin update failed",
            )
            if len(issues) < JellyfinWatchRestoreService.MAX_RETURNED_ISSUES:
                issues.append(issue)
            ImportBatchService.add_import_batch_error(
                session,
                import_batch_id=batch.import_batch_id,
                severity="error",
                entity_type="jellyfin_item",
                entity_ref=update_result.item_id,
                message=issue.reason,
                details={"title": issue.title},
            )

        error_count = len(update_results) - restored_count
        remaining_count = len(candidates) - restored_count
        status = (
            "completed"
            if remaining_count == 0 and error_count == 0
            else ("partial_with_errors" if error_count else "partial")
        )
        finalized = ImportBatchService.finish_import_batch(
            session,
            import_batch_id=batch.import_batch_id,
            status="completed_with_errors" if error_count else "completed",
            watch_events_inserted=0,
            media_items_inserted=0,
            media_versions_inserted=0,
            tags_added=0,
            errors_count=error_count,
            notes=payload.notes,
            parameters_patch={
                "attempted_count": len(update_results),
                "restored_count": restored_count,
                "remaining_count": remaining_count,
                "movie_candidate_count": movie_candidate_count,
                "episode_candidate_count": episode_candidate_count,
            },
        )
        return JellyfinWatchRestoreService._result(
            import_batch_id=finalized.import_batch_id,
            dry_run=False,
            status=status,
            eligible_count=len(eligible),
            candidate_count=len(candidates),
            attempted_count=len(update_results),
            restored_count=restored_count,
            movie_candidate_count=movie_candidate_count,
            episode_candidate_count=episode_candidate_count,
            error_count=error_count,
            issues=issues,
        )

    @staticmethod
    def _result(
        *,
        dry_run: bool,
        status: str,
        eligible_count: int,
        candidate_count: int,
        attempted_count: int,
        restored_count: int,
        movie_candidate_count: int,
        episode_candidate_count: int,
        error_count: int,
        issues: list[JellyfinWatchRestoreIssue],
        import_batch_id: UUID = UUID("00000000-0000-0000-0000-000000000000"),
    ) -> JellyfinWatchRestoreRead:
        return JellyfinWatchRestoreRead(
            import_batch_id=import_batch_id,
            status=status,
            dry_run=dry_run,
            eligible_count=eligible_count,
            already_played_count=eligible_count - candidate_count,
            candidate_count=candidate_count,
            attempted_count=attempted_count,
            restored_count=restored_count,
            remaining_count=candidate_count - restored_count,
            movie_candidate_count=movie_candidate_count,
            episode_candidate_count=episode_candidate_count,
            error_count=error_count,
            issues=issues,
        )
