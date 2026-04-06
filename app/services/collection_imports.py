from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.entities import CollectionEntry, MediaItem, Show
from app.repositories import collection as collection_repository
from app.repositories import import_batches as import_batch_repository
from app.repositories import media_items as media_item_repository
from app.repositories import shows as show_repository
from app.schemas.collection import JellyfinCollectionImportRequest
from app.services.import_batches import ImportBatchService
from app.services.jellyfin import JellyfinClient, JellyfinCollectionItem, JellyfinLibrary
from app.services.media_items import MediaItemService


@dataclass(frozen=True)
class JellyfinCollectionImportResult:
    import_batch_id: UUID
    status: str
    dry_run: bool
    processed_count: int
    inserted_count: int
    updated_count: int
    missing_marked_count: int
    skipped_count: int
    error_count: int
    media_items_created: int = 0
    shows_created: int = 0
    collection_entries_created: int = 0


@dataclass
class _SyncCounters:
    processed_count: int = 0
    inserted_count: int = 0
    updated_count: int = 0
    missing_marked_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    media_items_created: int = 0
    shows_created: int = 0
    collection_entries_created: int = 0


@dataclass
class _ResolvedShow:
    show: Show | None


@dataclass
class _ResolvedMediaItem:
    media_item: MediaItem | None


class JellyfinCollectionImportService:
    SOURCE = "jellyfin"

    @staticmethod
    def run_import(
        session: Session,
        *,
        payload: JellyfinCollectionImportRequest,
        client: JellyfinClient | None = None,
    ) -> JellyfinCollectionImportResult:
        jellyfin_client = client or JellyfinClient.from_settings()
        libraries = jellyfin_client.list_libraries()
        selected_libraries = JellyfinCollectionImportService._select_libraries(
            libraries=libraries,
            requested_ids=payload.library_ids,
        )

        items: list[JellyfinCollectionItem] = []
        for library in selected_libraries:
            items.extend(jellyfin_client.list_collection_items(library=library))

        items.sort(key=lambda item: (_type_order(item.item_type), item.library_name, item.title))
        seen_at = datetime.now(UTC)
        counters = _SyncCounters()
        seen_source_item_ids: set[str] = set()
        show_cache: dict[str, _ResolvedShow] = {}

        if payload.dry_run:
            for item in items:
                JellyfinCollectionImportService._sync_item(
                    session,
                    item=item,
                    seen_at=seen_at,
                    counters=counters,
                    seen_source_item_ids=seen_source_item_ids,
                    show_cache=show_cache,
                    import_batch_id=None,
                    dry_run=True,
                )
            counters.missing_marked_count = collection_repository.count_entries_to_mark_missing(
                session,
                source=JellyfinCollectionImportService.SOURCE,
                library_ids=[library.library_id for library in selected_libraries],
                seen_source_item_ids=seen_source_item_ids,
            )
            return JellyfinCollectionImportResult(
                import_batch_id=UUID("00000000-0000-0000-0000-000000000000"),
                status="dry_run",
                dry_run=True,
                processed_count=counters.processed_count,
                inserted_count=counters.inserted_count,
                updated_count=counters.updated_count,
                missing_marked_count=counters.missing_marked_count,
                skipped_count=counters.skipped_count,
                error_count=counters.error_count,
                media_items_created=counters.media_items_created,
                shows_created=counters.shows_created,
                collection_entries_created=counters.collection_entries_created,
            )

        source_detail = ",".join(sorted(library.library_id for library in selected_libraries))
        batch = ImportBatchService.start_import_batch(
            session,
            source=JellyfinCollectionImportService.SOURCE,
            source_detail=source_detail,
            notes=payload.notes,
            parameters={
                "library_ids": [library.library_id for library in selected_libraries],
                "library_names": [library.name for library in selected_libraries],
                "dry_run": False,
            },
        )

        try:
            for item in items:
                JellyfinCollectionImportService._sync_item(
                    session,
                    item=item,
                    seen_at=seen_at,
                    counters=counters,
                    seen_source_item_ids=seen_source_item_ids,
                    show_cache=show_cache,
                    import_batch_id=batch.import_batch_id,
                    dry_run=False,
                )

            counters.missing_marked_count = collection_repository.mark_missing_entries(
                session,
                source=JellyfinCollectionImportService.SOURCE,
                library_ids=[library.library_id for library in selected_libraries],
                seen_source_item_ids=seen_source_item_ids,
                missing_since=seen_at,
            )
            status = "completed_with_errors" if counters.error_count else "completed"
            ImportBatchService.finish_import_batch(
                session,
                import_batch_id=batch.import_batch_id,
                status=status,
                watch_events_inserted=0,
                media_items_inserted=counters.media_items_created,
                media_versions_inserted=0,
                tags_added=0,
                errors_count=counters.error_count,
                notes=payload.notes,
                parameters_patch={
                    "processed_count": counters.processed_count,
                    "inserted_count": counters.inserted_count,
                    "updated_count": counters.updated_count,
                    "missing_marked_count": counters.missing_marked_count,
                    "skipped_count": counters.skipped_count,
                    "shows_created": counters.shows_created,
                    "collection_entries_created": counters.collection_entries_created,
                },
            )
        except Exception:
            session.rollback()
            ImportBatchService.finish_import_batch(
                session,
                import_batch_id=batch.import_batch_id,
                status="failed",
                watch_events_inserted=0,
                media_items_inserted=counters.media_items_created,
                media_versions_inserted=0,
                tags_added=0,
                errors_count=counters.error_count + 1,
                notes=payload.notes,
                parameters_patch={
                    "processed_count": counters.processed_count,
                    "inserted_count": counters.inserted_count,
                    "updated_count": counters.updated_count,
                    "missing_marked_count": counters.missing_marked_count,
                    "skipped_count": counters.skipped_count,
                    "shows_created": counters.shows_created,
                    "collection_entries_created": counters.collection_entries_created,
                },
            )
            raise
        return JellyfinCollectionImportResult(
            import_batch_id=batch.import_batch_id,
            status=status,
            dry_run=False,
            processed_count=counters.processed_count,
            inserted_count=counters.inserted_count,
            updated_count=counters.updated_count,
            missing_marked_count=counters.missing_marked_count,
            skipped_count=counters.skipped_count,
            error_count=counters.error_count,
            media_items_created=counters.media_items_created,
            shows_created=counters.shows_created,
            collection_entries_created=counters.collection_entries_created,
        )

    @staticmethod
    def _select_libraries(
        *,
        libraries: list[JellyfinLibrary],
        requested_ids: list[str] | None,
    ) -> list[JellyfinLibrary]:
        if requested_ids:
            selected = [library for library in libraries if library.library_id in requested_ids]
            missing_ids = sorted(set(requested_ids) - {library.library_id for library in selected})
            if missing_ids:
                raise ValueError(f"Unknown Jellyfin library ids: {', '.join(missing_ids)}")
            return selected

        selected = [
            library
            for library in libraries
            if (library.collection_type or "").lower() in {"movies", "tvshows"}
        ]
        if not selected:
            raise ValueError("No Jellyfin movie or TV libraries were found")
        return selected

    @staticmethod
    def _sync_item(
        session: Session,
        *,
        item: JellyfinCollectionItem,
        seen_at: datetime,
        counters: _SyncCounters,
        seen_source_item_ids: set[str],
        show_cache: dict[str, _ResolvedShow],
        import_batch_id: UUID | None,
        dry_run: bool,
    ) -> None:
        counters.processed_count += 1
        seen_source_item_ids.add(item.source_item_id)

        try:
            with session.begin_nested():
                existing_entry = collection_repository.find_collection_entry_by_source_item(
                    session,
                    source=JellyfinCollectionImportService.SOURCE,
                    source_item_id=item.source_item_id,
                )
                media_item_id = None
                show_id = None

                if item.item_type == "show":
                    resolved_show = JellyfinCollectionImportService._resolve_show(
                        session,
                        item=item,
                        existing_entry=existing_entry,
                        counters=counters,
                        import_batch_id=import_batch_id,
                        dry_run=dry_run,
                    )
                    show_cache[item.source_item_id] = resolved_show
                    show_id = (
                        resolved_show.show.show_id if resolved_show.show is not None else None
                    )
                elif item.item_type == "movie":
                    resolved_media_item = JellyfinCollectionImportService._resolve_movie(
                        session,
                        item=item,
                        existing_entry=existing_entry,
                        counters=counters,
                        import_batch_id=import_batch_id,
                        dry_run=dry_run,
                    )
                    media_item_id = (
                        resolved_media_item.media_item.media_item_id
                        if resolved_media_item.media_item is not None
                        else None
                    )
                elif item.item_type == "episode":
                    resolved_media_item = JellyfinCollectionImportService._resolve_episode(
                        session,
                        item=item,
                        existing_entry=existing_entry,
                        counters=counters,
                        show_cache=show_cache,
                        import_batch_id=import_batch_id,
                        dry_run=dry_run,
                    )
                    media_item_id = (
                        resolved_media_item.media_item.media_item_id
                        if resolved_media_item.media_item is not None
                        else None
                    )

                if dry_run:
                    if existing_entry is None:
                        counters.inserted_count += 1
                        counters.collection_entries_created += 1
                    else:
                        counters.updated_count += 1
                    return

                if existing_entry is None:
                    collection_repository.create_collection_entry(
                        session,
                        source=JellyfinCollectionImportService.SOURCE,
                        source_item_id=item.source_item_id,
                        item_type=item.item_type,
                        library_id=item.library_id,
                        library_name=item.library_name,
                        media_item_id=media_item_id,
                        show_id=show_id,
                        seen_at=seen_at,
                        added_at=item.added_at,
                        runtime_seconds=item.runtime_seconds,
                        file_path=item.file_path,
                        source_data=item.source_data,
                    )
                    counters.inserted_count += 1
                    counters.collection_entries_created += 1
                else:
                    collection_repository.update_collection_entry(
                        session,
                        entry=existing_entry,
                        media_item_id=media_item_id,
                        show_id=show_id,
                        library_id=item.library_id,
                        library_name=item.library_name,
                        seen_at=seen_at,
                        added_at=item.added_at,
                        runtime_seconds=item.runtime_seconds,
                        file_path=item.file_path,
                        source_data=item.source_data,
                    )
                    counters.updated_count += 1
        except Exception as exc:
            counters.error_count += 1
            counters.skipped_count += 1
            if import_batch_id is not None:
                ImportBatchService.add_import_batch_error(
                    session,
                    import_batch_id=import_batch_id,
                    severity="error",
                    entity_type="collection_entry",
                    entity_ref=item.source_item_id,
                    message=str(exc),
                    details={
                        "item_type": item.item_type,
                        "library_id": item.library_id,
                        "title": item.title,
                    },
                )

    @staticmethod
    def _resolve_show(
        session: Session,
        *,
        item: JellyfinCollectionItem,
        existing_entry: CollectionEntry | None,
        counters: _SyncCounters,
        import_batch_id: UUID | None,
        dry_run: bool,
    ) -> _ResolvedShow:
        existing_show = None
        if existing_entry is not None and existing_entry.show_id is not None:
            existing_show = show_repository.find_show_by_id(session, show_id=existing_entry.show_id)
        if existing_show is None:
            existing_show = show_repository.find_show_by_external_ids(
                session,
                tmdb_id=item.tmdb_id,
                tvdb_id=item.tvdb_id,
                imdb_id=item.imdb_id,
            )
        if existing_show is None:
            existing_show = JellyfinCollectionImportService._resolve_show_by_title_year(
                session,
                title=item.title,
                year=item.year,
                import_batch_id=import_batch_id,
                source_item_id=item.source_item_id,
            )

        if existing_show is not None:
            safe_tmdb_id = JellyfinCollectionImportService._safe_show_tmdb_id(
                session,
                show=existing_show,
                tmdb_id=item.tmdb_id,
                import_batch_id=import_batch_id,
                source_item_id=item.source_item_id,
                title=item.title,
            )
            if not dry_run:
                show_repository.update_show(
                    session,
                    show=existing_show,
                    tmdb_id=safe_tmdb_id,
                    title=item.title.strip(),
                    year=item.year,
                    tvdb_id=item.tvdb_id,
                    imdb_id=item.imdb_id,
                )
            return _ResolvedShow(show=existing_show)

        counters.shows_created += 1
        if dry_run:
            return _ResolvedShow(show=None)

        safe_tmdb_id = JellyfinCollectionImportService._safe_show_tmdb_id(
            session,
            show=None,
            tmdb_id=item.tmdb_id,
            import_batch_id=import_batch_id,
            source_item_id=item.source_item_id,
            title=item.title,
        )
        created_show = show_repository.create_show(
            session,
            tmdb_id=safe_tmdb_id,
            title=item.title.strip(),
            year=item.year,
            tvdb_id=item.tvdb_id,
            imdb_id=item.imdb_id,
        )
        return _ResolvedShow(show=created_show)

    @staticmethod
    def _resolve_movie(
        session: Session,
        *,
        item: JellyfinCollectionItem,
        existing_entry: CollectionEntry | None,
        counters: _SyncCounters,
        import_batch_id: UUID | None,
        dry_run: bool,
    ) -> _ResolvedMediaItem:
        existing_media_item = None
        if existing_entry is not None and existing_entry.media_item_id is not None:
            existing_media_item = media_item_repository.get_media_item(
                session,
                media_item_id=existing_entry.media_item_id,
            )
        if existing_media_item is None:
            existing_media_item = media_item_repository.find_media_item_by_external_ids(
                session,
                media_type="movie",
                tmdb_id=item.tmdb_id,
                imdb_id=item.imdb_id,
                tvdb_id=item.tvdb_id,
            )
        if existing_media_item is None:
            existing_media_item = JellyfinCollectionImportService._resolve_media_item_by_title_year(
                session,
                media_type="movie",
                title=item.title,
                year=item.year,
                import_batch_id=import_batch_id,
                source_item_id=item.source_item_id,
            )

        if existing_media_item is not None:
            safe_ids = JellyfinCollectionImportService._safe_media_item_ids(
                session,
                media_item=existing_media_item,
                media_type="movie",
                tmdb_id=item.tmdb_id,
                imdb_id=item.imdb_id,
                tvdb_id=item.tvdb_id,
                import_batch_id=import_batch_id,
                source_item_id=item.source_item_id,
                title=item.title,
            )
            if not dry_run:
                state = MediaItemService.determine_initial_enrichment_state(
                    media_type="movie",
                    tmdb_id=safe_ids["tmdb_id"],
                    imdb_id=safe_ids["imdb_id"],
                    tvdb_id=safe_ids["tvdb_id"],
                    show_tmdb_id=None,
                )
                media_item_repository.update_media_item(
                    session,
                    media_item=existing_media_item,
                    title=item.title.strip(),
                    year=item.year,
                    tmdb_id=safe_ids["tmdb_id"],
                    imdb_id=safe_ids["imdb_id"],
                    tvdb_id=safe_ids["tvdb_id"],
                    base_runtime_seconds=item.runtime_seconds,
                    metadata_source="jellyfin",
                    enrichment_status=state.status,
                    enrichment_error=state.error,
                    jellyfin_item_id=item.source_item_id,
                )
            return _ResolvedMediaItem(media_item=existing_media_item)

        counters.media_items_created += 1
        if dry_run:
            return _ResolvedMediaItem(media_item=None)

        safe_ids = JellyfinCollectionImportService._safe_media_item_ids(
            session,
            media_item=None,
            media_type="movie",
            tmdb_id=item.tmdb_id,
            imdb_id=item.imdb_id,
            tvdb_id=item.tvdb_id,
            import_batch_id=import_batch_id,
            source_item_id=item.source_item_id,
            title=item.title,
        )
        state = MediaItemService.determine_initial_enrichment_state(
            media_type="movie",
            tmdb_id=safe_ids["tmdb_id"],
            imdb_id=safe_ids["imdb_id"],
            tvdb_id=safe_ids["tvdb_id"],
            show_tmdb_id=None,
        )
        created_media_item = media_item_repository.create_media_item(
            session,
            media_type="movie",
            title=item.title.strip(),
            year=item.year,
            tmdb_id=safe_ids["tmdb_id"],
            imdb_id=safe_ids["imdb_id"],
            tvdb_id=safe_ids["tvdb_id"],
            base_runtime_seconds=item.runtime_seconds,
            metadata_source="jellyfin",
            enrichment_status=state.status,
            enrichment_error=state.error,
            jellyfin_item_id=item.source_item_id,
        )
        return _ResolvedMediaItem(media_item=created_media_item)

    @staticmethod
    def _resolve_episode(
        session: Session,
        *,
        item: JellyfinCollectionItem,
        existing_entry: CollectionEntry | None,
        counters: _SyncCounters,
        show_cache: dict[str, _ResolvedShow],
        import_batch_id: UUID | None,
        dry_run: bool,
    ) -> _ResolvedMediaItem:
        if item.season_number is None or item.episode_number is None:
            raise ValueError("Episode items require season and episode numbers")

        resolved_show = JellyfinCollectionImportService._resolve_episode_show(
            session,
            item=item,
            show_cache=show_cache,
            counters=counters,
            import_batch_id=import_batch_id,
            dry_run=dry_run,
        )

        existing_media_item = None
        if existing_entry is not None and existing_entry.media_item_id is not None:
            existing_media_item = media_item_repository.get_media_item(
                session,
                media_item_id=existing_entry.media_item_id,
            )
        if existing_media_item is None and resolved_show.show is not None:
            existing_media_item = media_item_repository.find_episode_media_item_by_show_id(
                session,
                show_id=resolved_show.show.show_id,
                season_number=item.season_number,
                episode_number=item.episode_number,
            )
        if existing_media_item is None and item.show_tmdb_id is not None:
            existing_media_item = media_item_repository.find_episode_media_item(
                session,
                show_tmdb_id=item.show_tmdb_id,
                season_number=item.season_number,
                episode_number=item.episode_number,
            )
        if existing_media_item is None:
            existing_media_item = media_item_repository.find_media_item_by_external_ids(
                session,
                media_type="episode",
                tmdb_id=item.tmdb_id,
                imdb_id=item.imdb_id,
                tvdb_id=item.tvdb_id,
            )

        if existing_media_item is not None:
            safe_ids = JellyfinCollectionImportService._safe_media_item_ids(
                session,
                media_item=existing_media_item,
                media_type="episode",
                tmdb_id=item.tmdb_id,
                imdb_id=item.imdb_id,
                tvdb_id=item.tvdb_id,
                import_batch_id=import_batch_id,
                source_item_id=item.source_item_id,
                title=item.title,
            )
            if not dry_run:
                state = MediaItemService.determine_initial_enrichment_state(
                    media_type="episode",
                    tmdb_id=safe_ids["tmdb_id"],
                    imdb_id=safe_ids["imdb_id"],
                    tvdb_id=safe_ids["tvdb_id"],
                    show_tmdb_id=resolved_show.show.tmdb_id if resolved_show.show else item.show_tmdb_id,
                )
                media_item_repository.update_media_item(
                    session,
                    media_item=existing_media_item,
                    title=item.title.strip(),
                    year=item.year,
                    tmdb_id=safe_ids["tmdb_id"],
                    imdb_id=safe_ids["imdb_id"],
                    tvdb_id=safe_ids["tvdb_id"],
                    show_tmdb_id=resolved_show.show.tmdb_id if resolved_show.show else item.show_tmdb_id,
                    season_number=item.season_number,
                    episode_number=item.episode_number,
                    show_id=resolved_show.show.show_id if resolved_show.show else None,
                    base_runtime_seconds=item.runtime_seconds,
                    metadata_source="jellyfin",
                    enrichment_status=state.status,
                    enrichment_error=state.error,
                    jellyfin_item_id=item.source_item_id,
                )
            return _ResolvedMediaItem(media_item=existing_media_item)

        counters.media_items_created += 1
        if dry_run:
            return _ResolvedMediaItem(media_item=None)

        safe_ids = JellyfinCollectionImportService._safe_media_item_ids(
            session,
            media_item=None,
            media_type="episode",
            tmdb_id=item.tmdb_id,
            imdb_id=item.imdb_id,
            tvdb_id=item.tvdb_id,
            import_batch_id=import_batch_id,
            source_item_id=item.source_item_id,
            title=item.title,
        )
        state = MediaItemService.determine_initial_enrichment_state(
            media_type="episode",
            tmdb_id=safe_ids["tmdb_id"],
            imdb_id=safe_ids["imdb_id"],
            tvdb_id=safe_ids["tvdb_id"],
            show_tmdb_id=resolved_show.show.tmdb_id if resolved_show.show else item.show_tmdb_id,
        )
        created_media_item = media_item_repository.create_media_item(
            session,
            media_type="episode",
            title=item.title.strip(),
            year=item.year,
            tmdb_id=safe_ids["tmdb_id"],
            imdb_id=safe_ids["imdb_id"],
            tvdb_id=safe_ids["tvdb_id"],
            show_tmdb_id=resolved_show.show.tmdb_id if resolved_show.show else item.show_tmdb_id,
            season_number=item.season_number,
            episode_number=item.episode_number,
            show_id=resolved_show.show.show_id if resolved_show.show else None,
            base_runtime_seconds=item.runtime_seconds,
            metadata_source="jellyfin",
            enrichment_status=state.status,
            enrichment_error=state.error,
            jellyfin_item_id=item.source_item_id,
        )
        return _ResolvedMediaItem(media_item=created_media_item)

    @staticmethod
    def _resolve_episode_show(
        session: Session,
        *,
        item: JellyfinCollectionItem,
        show_cache: dict[str, _ResolvedShow],
        counters: _SyncCounters,
        import_batch_id: UUID | None,
        dry_run: bool,
    ) -> _ResolvedShow:
        if item.show_source_item_id and item.show_source_item_id in show_cache:
            return show_cache[item.show_source_item_id]

        synthetic_show = JellyfinCollectionItem(
            source_item_id=item.show_source_item_id or f"synthetic:{item.source_item_id}",
            item_type="show",
            library_id=item.library_id,
            library_name=item.library_name,
            title=item.show_title or "Unknown Show",
            year=item.show_year,
            tmdb_id=item.show_tmdb_id,
            imdb_id=item.show_imdb_id,
            tvdb_id=item.show_tvdb_id,
            season_number=None,
            episode_number=None,
            show_source_item_id=None,
            show_title=None,
            show_year=None,
            show_tmdb_id=None,
            show_imdb_id=None,
            show_tvdb_id=None,
            added_at=item.added_at,
            runtime_seconds=None,
            file_path=None,
            source_data={"synthetic": True, "from_episode_id": item.source_item_id},
        )
        existing_entry = None
        if item.show_source_item_id:
            existing_entry = collection_repository.find_collection_entry_by_source_item(
                session,
                source=JellyfinCollectionImportService.SOURCE,
                source_item_id=item.show_source_item_id,
            )
        resolved = JellyfinCollectionImportService._resolve_show(
            session,
            item=synthetic_show,
            existing_entry=existing_entry,
            counters=counters,
            import_batch_id=import_batch_id,
            dry_run=dry_run,
        )
        if item.show_source_item_id:
            show_cache[item.show_source_item_id] = resolved
        return resolved

    @staticmethod
    def _resolve_show_by_title_year(
        session: Session,
        *,
        title: str,
        year: int | None,
        import_batch_id: UUID | None,
        source_item_id: str,
    ) -> Show | None:
        if year is None:
            return None
        matches = show_repository.find_shows_by_title_and_year(session, title=title, year=year)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1 and import_batch_id is not None:
            ImportBatchService.add_import_batch_error(
                session,
                import_batch_id=import_batch_id,
                severity="warning",
                entity_type="show",
                entity_ref=source_item_id,
                message="Ambiguous title/year show match; creating a new show record",
                details={"title": title, "year": year},
            )
        return None

    @staticmethod
    def _safe_media_item_ids(
        session: Session,
        *,
        media_item: MediaItem | None,
        media_type: str,
        tmdb_id: int | None,
        imdb_id: str | None,
        tvdb_id: int | None,
        import_batch_id: UUID | None,
        source_item_id: str,
        title: str,
    ) -> dict[str, int | str | None]:
        safe_tmdb_id = tmdb_id
        if tmdb_id is not None:
            claimed = media_item_repository.find_media_item_by_tmdb_id(
                session,
                media_type=media_type,
                tmdb_id=tmdb_id,
            )
            if claimed is not None and (media_item is None or claimed.media_item_id != media_item.media_item_id):
                safe_tmdb_id = media_item.tmdb_id if media_item is not None else None
                JellyfinCollectionImportService._log_id_conflict(
                    session,
                    import_batch_id=import_batch_id,
                    source_item_id=source_item_id,
                    title=title,
                    field_name="tmdb_id",
                    field_value=str(tmdb_id),
                    claimed_title=claimed.title,
                )

        safe_imdb_id = imdb_id
        if imdb_id:
            claimed = media_item_repository.find_media_item_by_imdb_id(
                session,
                media_type=media_type,
                imdb_id=imdb_id,
            )
            if claimed is not None and (media_item is None or claimed.media_item_id != media_item.media_item_id):
                safe_imdb_id = media_item.imdb_id if media_item is not None else None
                JellyfinCollectionImportService._log_id_conflict(
                    session,
                    import_batch_id=import_batch_id,
                    source_item_id=source_item_id,
                    title=title,
                    field_name="imdb_id",
                    field_value=imdb_id,
                    claimed_title=claimed.title,
                )

        safe_tvdb_id = tvdb_id
        if tvdb_id is not None:
            claimed = media_item_repository.find_media_item_by_tvdb_id(
                session,
                media_type=media_type,
                tvdb_id=tvdb_id,
            )
            if claimed is not None and (media_item is None or claimed.media_item_id != media_item.media_item_id):
                safe_tvdb_id = media_item.tvdb_id if media_item is not None else None
                JellyfinCollectionImportService._log_id_conflict(
                    session,
                    import_batch_id=import_batch_id,
                    source_item_id=source_item_id,
                    title=title,
                    field_name="tvdb_id",
                    field_value=str(tvdb_id),
                    claimed_title=claimed.title,
                )

        return {
            "tmdb_id": safe_tmdb_id,
            "imdb_id": safe_imdb_id,
            "tvdb_id": safe_tvdb_id,
        }

    @staticmethod
    def _safe_show_tmdb_id(
        session: Session,
        *,
        show: Show | None,
        tmdb_id: int | None,
        import_batch_id: UUID | None,
        source_item_id: str,
        title: str,
    ) -> int | None:
        if tmdb_id is None:
            return show.tmdb_id if show is not None else None
        claimed = show_repository.find_show_by_tmdb_id(session, tmdb_id=tmdb_id)
        if claimed is None or (show is not None and claimed.show_id == show.show_id):
            return tmdb_id
        JellyfinCollectionImportService._log_id_conflict(
            session,
            import_batch_id=import_batch_id,
            source_item_id=source_item_id,
            title=title,
            field_name="tmdb_id",
            field_value=str(tmdb_id),
            claimed_title=claimed.title,
        )
        return show.tmdb_id if show is not None else None

    @staticmethod
    def _log_id_conflict(
        session: Session,
        *,
        import_batch_id: UUID | None,
        source_item_id: str,
        title: str,
        field_name: str,
        field_value: str,
        claimed_title: str,
    ) -> None:
        if import_batch_id is None:
            return
        batch = import_batch_repository.get_import_batch(
            session,
            import_batch_id=import_batch_id,
        )
        if batch is None:
            return
        import_batch_repository.create_import_batch_error(
            session,
            import_batch=batch,
            severity="warning",
            entity_type="collection_entry",
            entity_ref=source_item_id,
            message=f"Skipped conflicting {field_name} during collection import",
            details={
                "title": title,
                "field_name": field_name,
                "field_value": field_value,
                "claimed_by": claimed_title,
            },
        )

    @staticmethod
    def _resolve_media_item_by_title_year(
        session: Session,
        *,
        media_type: str,
        title: str,
        year: int | None,
        import_batch_id: UUID | None,
        source_item_id: str,
    ) -> MediaItem | None:
        if year is None:
            return None
        matches = media_item_repository.find_media_items_by_title_and_year(
            session,
            media_type=media_type,
            title=title,
            year=year,
        )
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1 and import_batch_id is not None:
            ImportBatchService.add_import_batch_error(
                session,
                import_batch_id=import_batch_id,
                severity="warning",
                entity_type="media_item",
                entity_ref=source_item_id,
                message="Ambiguous title/year media match; creating a new media record",
                details={"media_type": media_type, "title": title, "year": year},
            )
        return None


def _type_order(item_type: str) -> int:
    return {"show": 0, "movie": 1, "episode": 2}.get(item_type, 99)
