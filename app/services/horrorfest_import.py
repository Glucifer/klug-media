from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, time, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import watch_events as watch_event_repository
from app.schemas.horrorfest_import import (
    HorrorfestPreserveImportSummary,
    HorrorfestPreserveRow,
)
from app.services.horrorfest import HorrorfestService


class HorrorfestImportService:
    VERSION_NAME_MAP = {
        "alt": "Alternate Cut",
        "ldi": "Last Drive-In",
    }

    @staticmethod
    def run_preserve_import(
        session: Session,
        *,
        user_id: UUID,
        rows: list[HorrorfestPreserveRow],
        dry_run: bool,
        updated_by: str,
    ) -> HorrorfestPreserveImportSummary:
        normalized_updated_by = updated_by.strip()
        if not normalized_updated_by:
            raise ValueError("updated_by must not be empty")

        year_configs_created = HorrorfestImportService._ensure_year_configs(
            session,
            rows=rows,
            dry_run=dry_run,
        )

        matched_count = 0
        updated_count = 0
        error_count = 0
        unmatched_rows: list[dict] = []

        for row in rows:
            watch_event = HorrorfestImportService._match_watch_event(
                session,
                user_id=user_id,
                row=row,
            )
            if watch_event is None:
                error_count += 1
                unmatched_rows.append(
                    {
                        "trakt_log_id": row.trakt_log_id,
                        "tmdb_id": row.tmdb_id,
                        "watched_at": row.watched_at.isoformat(),
                        "watch_year": row.watch_year,
                        "watch_order": row.watch_order,
                        "alternate_version": row.alternate_version,
                    }
                )
                continue

            matched_count += 1
            if dry_run:
                updated_count += 1
                continue

            changed = HorrorfestImportService._apply_preserved_horrorfest_metadata(
                session,
                watch_id=watch_event.watch_id,
                row=row,
                updated_by=normalized_updated_by,
            )
            if changed:
                updated_count += 1

        return HorrorfestPreserveImportSummary(
            processed_count=len(rows),
            matched_count=matched_count,
            updated_count=updated_count,
            error_count=error_count,
            year_configs_created=year_configs_created,
            unmatched_rows=unmatched_rows,
        )

    @staticmethod
    def _ensure_year_configs(
        session: Session,
        *,
        rows: list[HorrorfestPreserveRow],
        dry_run: bool,
    ) -> int:
        by_year: dict[int, list[HorrorfestPreserveRow]] = defaultdict(list)
        for row in rows:
            by_year[row.watch_year].append(row)

        created = 0
        for watch_year, year_rows in by_year.items():
            existing = next(
                (item for item in HorrorfestService.list_years(session) if item["horrorfest_year"] == watch_year),
                None,
            )
            if existing is not None:
                continue
            created += 1
            if dry_run:
                continue
            min_date = min(row.watched_at for row in year_rows)
            max_date = max(row.watched_at for row in year_rows)
            HorrorfestService.upsert_year_config(
                session,
                horrorfest_year=watch_year,
                window_start_at=datetime.combine(min_date, time.min, tzinfo=UTC),
                window_end_at=datetime.combine(max_date, time.max, tzinfo=UTC),
                label=f"Horrorfest {watch_year}",
                notes="Auto-created from preserved Horrorfest import",
                is_active=False,
            )
        return created

    @staticmethod
    def _match_watch_event(
        session: Session,
        *,
        user_id: UUID,
        row: HorrorfestPreserveRow,
    ):
        matched = watch_event_repository.find_user_watch_event_by_source_event_id(
            session,
            user_id=user_id,
            source_event_id=row.trakt_log_id,
        )
        if matched is not None:
            return matched

        fallback_rows = watch_event_repository.list_user_movie_watch_events_by_tmdb_and_local_date(
            session,
            user_id=user_id,
            tmdb_id=row.tmdb_id,
            local_date=row.watched_at,
        )
        if len(fallback_rows) == 1:
            return fallback_rows[0]

        nearby_match = HorrorfestImportService._match_by_nearby_local_date(
            session,
            user_id=user_id,
            row=row,
        )
        if nearby_match is not None:
            return nearby_match

        ordered_match = HorrorfestImportService._match_by_year_watch_order(
            session,
            user_id=user_id,
            row=row,
        )
        if ordered_match is not None:
            return ordered_match
        return None

    @staticmethod
    def _match_by_nearby_local_date(
        session: Session,
        *,
        user_id: UUID,
        row: HorrorfestPreserveRow,
    ):
        candidates: dict[UUID, object] = {}
        for offset in (-1, 1):
            candidate_date = row.watched_at + timedelta(days=offset)
            nearby_rows = watch_event_repository.list_user_movie_watch_events_by_tmdb_and_local_date(
                session,
                user_id=user_id,
                tmdb_id=row.tmdb_id,
                local_date=candidate_date,
            )
            for watch_event in nearby_rows:
                candidates[watch_event.watch_id] = watch_event
        if len(candidates) == 1:
            return next(iter(candidates.values()))
        return None

    @staticmethod
    def _match_by_year_watch_order(
        session: Session,
        *,
        user_id: UUID,
        row: HorrorfestPreserveRow,
    ):
        year_watch_events = watch_event_repository.list_user_movie_watch_events_by_local_year(
            session,
            user_id=user_id,
            local_year=row.watch_year,
        )
        target_index = row.watch_order - 1
        if target_index < 0 or target_index >= len(year_watch_events):
            return None
        candidate = year_watch_events[target_index]
        media_item = getattr(candidate, "media_item", None)
        if media_item is None or media_item.tmdb_id != row.tmdb_id:
            return None
        return candidate

    @staticmethod
    def _apply_preserved_horrorfest_metadata(
        session: Session,
        *,
        watch_id,
        row: HorrorfestPreserveRow,
        updated_by: str,
    ) -> bool:
        watch_event = watch_event_repository.get_watch_event(session, watch_id=watch_id)
        if watch_event is None:
            raise ValueError(f"Watch event '{watch_id}' not found")
        changed = False
        rating_value = int(row.watch_rating) if row.watch_rating is not None else None
        if rating_value is not None:
            watch_event.rating_value = rating_value
            watch_event.rating_scale = "10-star"
            watch_event.updated_by = updated_by
            watch_event.update_reason = "Imported preserved Horrorfest rating"
            watch_event.updated_at = datetime.now(UTC)
            changed = True

        version_name, runtime_minutes = HorrorfestImportService._map_version_override(row)
        if version_name is not None or runtime_minutes is not None:
            watch_event.watch_version_name = version_name
            watch_event.watch_runtime_seconds = (
                runtime_minutes * 60 if runtime_minutes is not None else None
            )
            watch_event.updated_by = updated_by
            watch_event.update_reason = "Imported preserved Horrorfest version"
            watch_event.updated_at = datetime.now(UTC)
            watch_event.dedupe_hash = None
            watch_event_repository.update_watch_event(session, watch_event=watch_event)
            changed = True

        if changed and version_name is None and rating_value is not None:
            watch_event_repository.update_watch_event(session, watch_event=watch_event)

        HorrorfestService.include_watch_event(
            session,
            watch_id=watch_id,
            horrorfest_year=row.watch_year,
            updated_by=updated_by,
            update_reason="Imported preserved Horrorfest assignment",
            target_order=row.watch_order,
            source_kind="auto_import",
            commit=False,
        )
        session.commit()
        changed = True
        return changed

    @staticmethod
    def _map_version_override(
        row: HorrorfestPreserveRow,
    ) -> tuple[str | None, int | None]:
        alt = (row.alternate_version or "").strip().lower()
        if alt in {"", "std"}:
            return None, None
        runtime_minutes = row.runtime_used
        return HorrorfestImportService.VERSION_NAME_MAP.get(alt, "Alternate Version"), runtime_minutes
