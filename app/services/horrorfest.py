from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.datetime_utils import ensure_timezone_aware
from app.db.models.entities import HorrorfestEntry, HorrorfestYear, MediaItem, WatchEvent
from app.repositories import horrorfest as horrorfest_repository
from app.repositories import watch_events as watch_event_repository


class HorrorfestConstraintError(Exception):
    """Raised when a Horrorfest update violates constraints."""


class HorrorfestService:
    AUTO_SOURCE_KINDS = {
        "live_playback": "auto_live",
        "manual_import": "auto_import",
        "manual_entry": "manual",
    }

    @staticmethod
    def list_years(session: Session) -> list[dict[str, object]]:
        return horrorfest_repository.list_horrorfest_years(session)

    @staticmethod
    def upsert_year_config(
        session: Session,
        *,
        horrorfest_year: int,
        window_start_at: datetime,
        window_end_at: datetime,
        label: str | None,
        notes: str | None,
        is_active: bool,
    ) -> HorrorfestYear:
        normalized_start = ensure_timezone_aware(
            window_start_at, field_name="window_start_at"
        ).astimezone(UTC)
        normalized_end = ensure_timezone_aware(
            window_end_at, field_name="window_end_at"
        ).astimezone(UTC)
        if normalized_end <= normalized_start:
            raise ValueError("window_end_at must be after window_start_at")

        overlap = horrorfest_repository.find_overlapping_horrorfest_year(
            session,
            window_start_at=normalized_start,
            window_end_at=normalized_end,
            exclude_year=horrorfest_year,
        )
        if overlap is not None:
            raise ValueError(
                f"Horrorfest year window overlaps configured year {overlap.horrorfest_year}"
            )

        existing = horrorfest_repository.get_horrorfest_year(
            session, horrorfest_year=horrorfest_year
        )
        now = datetime.now(UTC)
        if existing is None:
            year_config = horrorfest_repository.create_horrorfest_year(
                session,
                horrorfest_year=horrorfest_year,
                window_start_at=normalized_start,
                window_end_at=normalized_end,
                label=HorrorfestService._normalize_optional_text(label),
                notes=HorrorfestService._normalize_optional_text(notes),
                is_active=is_active,
                updated_at=now,
            )
        else:
            existing.window_start_at = normalized_start
            existing.window_end_at = normalized_end
            existing.label = HorrorfestService._normalize_optional_text(label)
            existing.notes = HorrorfestService._normalize_optional_text(notes)
            existing.is_active = is_active
            existing.updated_at = now
            year_config = horrorfest_repository.update_horrorfest_year(
                session, year_config=existing
            )

        try:
            session.commit()
            return year_config
        except IntegrityError as exc:
            session.rollback()
            raise HorrorfestConstraintError(
                "Horrorfest year failed database constraints"
            ) from exc

    @staticmethod
    def list_entries(
        session: Session,
        *,
        horrorfest_year: int,
        include_removed: bool,
    ) -> list[dict[str, object]]:
        year_config = horrorfest_repository.get_horrorfest_year(
            session, horrorfest_year=horrorfest_year
        )
        if year_config is None:
            raise ValueError(f"Horrorfest year '{horrorfest_year}' not found")
        return horrorfest_repository.list_horrorfest_entries(
            session,
            horrorfest_year=horrorfest_year,
            include_removed=include_removed,
        )

    @staticmethod
    def list_analytics_years(
        session: Session,
        *,
        user_id: UUID | None = None,
    ) -> list[dict[str, object]]:
        return horrorfest_repository.list_horrorfest_analytics_years(
            session,
            user_id=user_id,
        )

    @staticmethod
    def get_analytics_year_detail(
        session: Session,
        *,
        horrorfest_year: int,
        user_id: UUID | None = None,
    ) -> dict[str, object]:
        detail = horrorfest_repository.get_horrorfest_analytics_year_detail(
            session,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )
        if detail is None:
            raise ValueError(f"Horrorfest year '{horrorfest_year}' not found")
        return detail

    @staticmethod
    def get_analytics_title_matrix(
        session: Session,
        *,
        user_id: UUID | None = None,
    ) -> dict[str, object]:
        return horrorfest_repository.list_horrorfest_analytics_title_matrix(
            session,
            user_id=user_id,
        )

    @staticmethod
    def get_analytics_decade_matrix(
        session: Session,
        *,
        user_id: UUID | None = None,
    ) -> dict[str, object]:
        return horrorfest_repository.list_horrorfest_analytics_decade_matrix(
            session,
            user_id=user_id,
        )

    @staticmethod
    def get_analytics_comparison(
        session: Session,
        *,
        left_year: int,
        right_year: int,
        user_id: UUID | None = None,
    ) -> dict[str, object]:
        if left_year == right_year:
            raise ValueError("left_year and right_year must be different")
        detail = horrorfest_repository.get_horrorfest_analytics_comparison(
            session,
            left_year=left_year,
            right_year=right_year,
            user_id=user_id,
        )
        if detail is None:
            raise ValueError("One or both Horrorfest years were not found")
        return detail

    @staticmethod
    def get_analytics_repeated_titles(
        session: Session,
        *,
        user_id: UUID | None = None,
    ) -> dict[str, object]:
        return horrorfest_repository.list_horrorfest_analytics_repeated_titles(
            session,
            user_id=user_id,
        )

    @staticmethod
    def get_analytics_highest_rated_titles(
        session: Session,
        *,
        user_id: UUID | None = None,
        minimum_repeat_count: int = 2,
    ) -> list[dict[str, object]]:
        return horrorfest_repository.list_horrorfest_analytics_highest_rated_titles(
            session,
            user_id=user_id,
            minimum_repeat_count=minimum_repeat_count,
        )

    @staticmethod
    def get_analytics_rewatch_leaderboard(
        session: Session,
        *,
        user_id: UUID | None = None,
    ) -> list[dict[str, object]]:
        return horrorfest_repository.list_horrorfest_analytics_rewatch_leaderboard(
            session,
            user_id=user_id,
        )

    @staticmethod
    def list_analytics_title_entries(
        session: Session,
        *,
        media_item_id: UUID,
        horrorfest_year: int | None = None,
        user_id: UUID | None = None,
    ) -> list[dict[str, object]]:
        return horrorfest_repository.list_horrorfest_title_entries(
            session,
            media_item_id=media_item_id,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )

    @staticmethod
    def list_analytics_decade_entries(
        session: Session,
        *,
        decade_start: int,
        horrorfest_year: int | None = None,
        user_id: UUID | None = None,
    ) -> list[dict[str, object]]:
        if decade_start % 10 != 0:
            raise ValueError("decade_start must be a decade boundary")
        return horrorfest_repository.list_horrorfest_decade_entries(
            session,
            decade_start=decade_start,
            horrorfest_year=horrorfest_year,
            user_id=user_id,
        )

    @staticmethod
    def list_analytics_year_entries(
        session: Session,
        *,
        horrorfest_year: int,
        watch_date: date | None = None,
        playback_source: str | None = None,
        rating_value: Decimal | None = None,
        user_id: UUID | None = None,
    ) -> list[dict[str, object]]:
        HorrorfestService._get_year_or_raise(session, horrorfest_year=horrorfest_year)
        normalized_playback_source = HorrorfestService._normalize_optional_text(playback_source)
        if rating_value is not None and rating_value < 0:
            raise ValueError("rating_value must be zero or greater")
        return horrorfest_repository.list_horrorfest_year_entries(
            session,
            horrorfest_year=horrorfest_year,
            watch_date=watch_date,
            playback_source=normalized_playback_source,
            rating_value=rating_value,
            user_id=user_id,
        )

    @staticmethod
    def sync_watch_event(
        session: Session,
        *,
        watch_event: WatchEvent,
    ) -> None:
        year_config = HorrorfestService._qualifying_year_config(
            session, watch_event=watch_event
        )
        existing_active = horrorfest_repository.get_active_horrorfest_entry_for_watch(
            session,
            watch_id=watch_event.watch_id,
        )
        if year_config is None:
            if existing_active is not None:
                HorrorfestService._soft_remove_entry(
                    session,
                    entry=existing_active,
                    updated_by=watch_event.updated_by,
                    update_reason=watch_event.update_reason,
                )
                HorrorfestService._normalize_year_orders(
                    session,
                    horrorfest_year=existing_active.horrorfest_year,
                )
            return

        source_kind = HorrorfestService.AUTO_SOURCE_KINDS.get(
            watch_event.origin_kind, "manual"
        )
        if existing_active is not None and existing_active.horrorfest_year == year_config.horrorfest_year:
            HorrorfestService._rebuild_year_orders_by_watched_at(
                session,
                horrorfest_year=year_config.horrorfest_year,
            )
            return

        if existing_active is not None:
            previous_year = existing_active.horrorfest_year
            HorrorfestService._soft_remove_entry(
                session,
                entry=existing_active,
                updated_by=watch_event.updated_by,
                update_reason=watch_event.update_reason,
            )
            HorrorfestService._normalize_year_orders(
                session,
                horrorfest_year=previous_year,
            )

        HorrorfestService._activate_watch_for_year(
            session,
            watch_event=watch_event,
            horrorfest_year=year_config.horrorfest_year,
            source_kind=source_kind,
            updated_by=watch_event.updated_by,
            update_reason=watch_event.update_reason,
            target_order=None,
        )

    @staticmethod
    def include_watch_event(
        session: Session,
        *,
        watch_id: UUID,
        horrorfest_year: int,
        updated_by: str,
        update_reason: str | None,
        target_order: int | None,
        source_kind: str = "manual",
        commit: bool = True,
    ) -> HorrorfestEntry:
        watch_event = HorrorfestService._get_watch_event_or_raise(
            session, watch_id=watch_id
        )
        if watch_event.is_deleted:
            raise ValueError("Cannot include a deleted watch event in Horrorfest")
        normalized_updated_by = HorrorfestService._normalize_required_text(
            updated_by, field_name="updated_by"
        )
        normalized_reason = HorrorfestService._normalize_optional_text(update_reason)
        year_config = HorrorfestService._get_year_or_raise(
            session, horrorfest_year=horrorfest_year
        )
        HorrorfestService._validate_watch_eligibility(
            session,
            watch_event=watch_event,
            year_config=year_config,
        )

        active_entry = horrorfest_repository.get_active_horrorfest_entry_for_watch(
            session, watch_id=watch_id
        )
        if active_entry is not None and active_entry.horrorfest_year != horrorfest_year:
            previous_year = active_entry.horrorfest_year
            HorrorfestService._soft_remove_entry(
                session,
                entry=active_entry,
                updated_by=normalized_updated_by,
                update_reason=normalized_reason,
            )
            HorrorfestService._normalize_year_orders(
                session,
                horrorfest_year=previous_year,
            )

        entry = HorrorfestService._activate_watch_for_year(
            session,
            watch_event=watch_event,
            horrorfest_year=horrorfest_year,
            source_kind=source_kind,
            updated_by=normalized_updated_by,
            update_reason=normalized_reason,
            target_order=target_order,
        )
        try:
            if commit:
                session.commit()
            return entry
        except IntegrityError as exc:
            session.rollback()
            raise HorrorfestConstraintError(
                "Horrorfest entry failed database constraints"
            ) from exc

    @staticmethod
    def remove_entry(
        session: Session,
        *,
        horrorfest_entry_id: UUID,
        updated_by: str,
        update_reason: str | None,
    ) -> HorrorfestEntry:
        entry = HorrorfestService._get_entry_or_raise(
            session, horrorfest_entry_id=horrorfest_entry_id
        )
        if entry.is_removed:
            raise ValueError("Horrorfest entry is already removed")
        HorrorfestService._soft_remove_entry(
            session,
            entry=entry,
            updated_by=HorrorfestService._normalize_required_text(
                updated_by, field_name="updated_by"
            ),
            update_reason=HorrorfestService._normalize_optional_text(update_reason),
        )
        HorrorfestService._normalize_year_orders(
            session,
            horrorfest_year=entry.horrorfest_year,
        )
        try:
            session.commit()
            return entry
        except IntegrityError as exc:
            session.rollback()
            raise HorrorfestConstraintError(
                "Horrorfest entry failed database constraints"
            ) from exc

    @staticmethod
    def restore_entry(
        session: Session,
        *,
        horrorfest_entry_id: UUID,
        updated_by: str,
        update_reason: str | None,
    ) -> HorrorfestEntry:
        entry = HorrorfestService._get_entry_or_raise(
            session, horrorfest_entry_id=horrorfest_entry_id
        )
        if not entry.is_removed:
            raise ValueError("Horrorfest entry is not removed")
        return HorrorfestService.include_watch_event(
            session,
            watch_id=entry.watch_id,
            horrorfest_year=entry.horrorfest_year,
            updated_by=updated_by,
            update_reason=update_reason,
            target_order=None,
            source_kind=entry.source_kind,
            commit=True,
        )

    @staticmethod
    def move_entry(
        session: Session,
        *,
        horrorfest_entry_id: UUID,
        updated_by: str,
        update_reason: str | None,
        target_order: int,
    ) -> HorrorfestEntry:
        entry = HorrorfestService._get_entry_or_raise(
            session, horrorfest_entry_id=horrorfest_entry_id
        )
        if entry.is_removed:
            raise ValueError("Cannot move a removed Horrorfest entry")
        normalized_updated_by = HorrorfestService._normalize_required_text(
            updated_by, field_name="updated_by"
        )
        normalized_reason = HorrorfestService._normalize_optional_text(update_reason)
        active_entries = horrorfest_repository.list_active_horrorfest_entries_for_year(
            session,
            horrorfest_year=entry.horrorfest_year,
        )
        active_entries = [
            candidate
            for candidate in active_entries
            if candidate.horrorfest_entry_id != entry.horrorfest_entry_id
        ]
        insertion_index = max(0, min(target_order - 1, len(active_entries)))
        active_entries.insert(insertion_index, entry)
        entry.updated_at = datetime.now(UTC)
        entry.updated_by = normalized_updated_by
        entry.update_reason = normalized_reason
        HorrorfestService._apply_ordered_entries(
            session,
            horrorfest_year=entry.horrorfest_year,
            ordered_entries=active_entries,
        )
        try:
            session.commit()
            return entry
        except IntegrityError as exc:
            session.rollback()
            raise HorrorfestConstraintError(
                "Horrorfest entry failed database constraints"
            ) from exc

    @staticmethod
    def _activate_watch_for_year(
        session: Session,
        *,
        watch_event: WatchEvent,
        horrorfest_year: int,
        source_kind: str,
        updated_by: str | None,
        update_reason: str | None,
        target_order: int | None,
    ) -> HorrorfestEntry:
        existing = horrorfest_repository.get_horrorfest_entry_for_watch_and_year(
            session,
            watch_id=watch_event.watch_id,
            horrorfest_year=horrorfest_year,
        )
        now = datetime.now(UTC)
        if existing is None:
            entry = horrorfest_repository.create_horrorfest_entry(
                session,
                watch_id=watch_event.watch_id,
                horrorfest_year=horrorfest_year,
                watch_order=None,
                source_kind=source_kind,
                updated_at=now,
                updated_by=updated_by,
                update_reason=update_reason,
            )
        else:
            existing.is_removed = False
            existing.removed_at = None
            existing.removed_by = None
            existing.removed_reason = None
            existing.source_kind = source_kind
            existing.updated_at = now
            existing.updated_by = updated_by
            existing.update_reason = update_reason
            entry = horrorfest_repository.update_horrorfest_entry(
                session, entry=existing
            )

        active_entries = horrorfest_repository.list_active_horrorfest_entries_for_year(
            session,
            horrorfest_year=horrorfest_year,
        )
        if entry.horrorfest_entry_id not in {
            candidate.horrorfest_entry_id for candidate in active_entries
        }:
            active_entries.append(entry)

        if target_order is None:
            active_entries.sort(
                key=lambda candidate: (
                    HorrorfestService._get_watch_event_or_raise(
                        session, watch_id=candidate.watch_id
                    ).watched_at,
                    candidate.created_at,
                    candidate.horrorfest_entry_id,
                )
            )
        else:
            active_entries = [
                candidate
                for candidate in active_entries
                if candidate.horrorfest_entry_id != entry.horrorfest_entry_id
            ]
            insert_at = max(0, min(target_order - 1, len(active_entries)))
            active_entries.insert(insert_at, entry)

        HorrorfestService._apply_ordered_entries(
            session,
            horrorfest_year=horrorfest_year,
            ordered_entries=active_entries,
        )
        return entry

    @staticmethod
    def _apply_ordered_entries(
        session: Session,
        *,
        horrorfest_year: int,
        ordered_entries: list[HorrorfestEntry],
    ) -> None:
        for index, entry in enumerate(ordered_entries, start=1):
            entry.watch_order = -index
            session.add(entry)
        session.flush()
        for index, entry in enumerate(ordered_entries, start=1):
            entry.watch_order = index
            session.add(entry)
        session.flush()

    @staticmethod
    def _normalize_year_orders(
        session: Session,
        *,
        horrorfest_year: int,
    ) -> None:
        active_entries = horrorfest_repository.list_active_horrorfest_entries_for_year(
            session,
            horrorfest_year=horrorfest_year,
        )
        active_entries.sort(
            key=lambda candidate: (
                candidate.watch_order if candidate.watch_order is not None else 10**9,
                HorrorfestService._get_watch_event_or_raise(
                    session, watch_id=candidate.watch_id
                ).watched_at,
                candidate.created_at,
                candidate.horrorfest_entry_id,
            )
        )
        HorrorfestService._apply_ordered_entries(
            session,
            horrorfest_year=horrorfest_year,
            ordered_entries=active_entries,
        )

    @staticmethod
    def _rebuild_year_orders_by_watched_at(
        session: Session,
        *,
        horrorfest_year: int,
    ) -> None:
        active_entries = horrorfest_repository.list_active_horrorfest_entries_for_year(
            session,
            horrorfest_year=horrorfest_year,
        )
        active_entries.sort(
            key=lambda candidate: (
                HorrorfestService._get_watch_event_or_raise(
                    session, watch_id=candidate.watch_id
                ).watched_at,
                candidate.created_at,
                candidate.horrorfest_entry_id,
            )
        )
        HorrorfestService._apply_ordered_entries(
            session,
            horrorfest_year=horrorfest_year,
            ordered_entries=active_entries,
        )

    @staticmethod
    def _soft_remove_entry(
        session: Session,
        *,
        entry: HorrorfestEntry,
        updated_by: str | None,
        update_reason: str | None,
    ) -> HorrorfestEntry:
        now = datetime.now(UTC)
        entry.is_removed = True
        entry.watch_order = None
        entry.removed_at = now
        entry.removed_by = updated_by
        entry.removed_reason = update_reason
        entry.updated_at = now
        entry.updated_by = updated_by
        entry.update_reason = update_reason
        return horrorfest_repository.update_horrorfest_entry(session, entry=entry)

    @staticmethod
    def _qualifying_year_config(
        session: Session,
        *,
        watch_event: WatchEvent,
    ) -> HorrorfestYear | None:
        if not HorrorfestService._is_watch_eligible(session, watch_event=watch_event):
            return None
        return horrorfest_repository.find_horrorfest_year_for_timestamp(
            session,
            watched_at=watch_event.watched_at,
        )

    @staticmethod
    def _validate_watch_eligibility(
        session: Session,
        *,
        watch_event: WatchEvent,
        year_config: HorrorfestYear,
    ) -> None:
        if not HorrorfestService._is_watch_eligible(session, watch_event=watch_event):
            raise ValueError(
                "Only non-deleted completed movie watch events can be included in Horrorfest"
            )
        if not (
            year_config.window_start_at <= watch_event.watched_at <= year_config.window_end_at
        ):
            raise ValueError(
                "Watch event watched_at must fall inside the configured Horrorfest year window"
            )

    @staticmethod
    def _is_watch_eligible(
        session: Session,
        *,
        watch_event: WatchEvent,
    ) -> bool:
        if watch_event.is_deleted or not watch_event.completed:
            return False
        media_item = session.get(MediaItem, watch_event.media_item_id)
        return media_item is not None and media_item.type == "movie"

    @staticmethod
    def _get_year_or_raise(
        session: Session,
        *,
        horrorfest_year: int,
    ) -> HorrorfestYear:
        year_config = horrorfest_repository.get_horrorfest_year(
            session, horrorfest_year=horrorfest_year
        )
        if year_config is None:
            raise ValueError(f"Horrorfest year '{horrorfest_year}' not found")
        return year_config

    @staticmethod
    def _get_entry_or_raise(
        session: Session,
        *,
        horrorfest_entry_id: UUID,
    ) -> HorrorfestEntry:
        entry = horrorfest_repository.get_horrorfest_entry(
            session, horrorfest_entry_id=horrorfest_entry_id
        )
        if entry is None:
            raise ValueError(f"Horrorfest entry '{horrorfest_entry_id}' not found")
        return entry

    @staticmethod
    def _get_watch_event_or_raise(
        session: Session,
        *,
        watch_id: UUID,
    ) -> WatchEvent:
        watch_event = watch_event_repository.get_watch_event(session, watch_id=watch_id)
        if watch_event is None:
            raise ValueError(f"Watch event '{watch_id}' not found")
        return watch_event

    @staticmethod
    def _normalize_required_text(value: str, *, field_name: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} must not be empty")
        return normalized

    @staticmethod
    def _normalize_optional_text(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None
