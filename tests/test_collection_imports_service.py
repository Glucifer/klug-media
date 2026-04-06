from types import SimpleNamespace
from uuid import uuid4

from app.schemas.collection import JellyfinCollectionImportRequest
from app.services.collection_imports import JellyfinCollectionImportService
from app.services.jellyfin import JellyfinCollectionItem, JellyfinLibrary


class DummyNestedTransaction:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummySession:
    def __init__(self) -> None:
        self.rollback_calls = 0

    def begin_nested(self):
        return DummyNestedTransaction()

    def rollback(self):
        self.rollback_calls += 1
        return None


class DummyClient:
    def __init__(self, libraries, items_by_library) -> None:
        self._libraries = libraries
        self._items_by_library = items_by_library

    def list_libraries(self):
        return self._libraries

    def list_collection_items(self, *, library):
        return list(self._items_by_library.get(library.library_id, []))


def _movie_item(*, source_item_id: str = "movie-1") -> JellyfinCollectionItem:
    return JellyfinCollectionItem(
        source_item_id=source_item_id,
        item_type="movie",
        library_id="movies",
        library_name="Movies",
        title="Alien",
        year=1979,
        tmdb_id=348,
        imdb_id="tt0078748",
        tvdb_id=None,
        season_number=None,
        episode_number=None,
        show_source_item_id=None,
        show_title=None,
        show_year=None,
        show_tmdb_id=None,
        show_imdb_id=None,
        show_tvdb_id=None,
        added_at=None,
        runtime_seconds=7020,
        file_path="D:/media/Alien.mkv",
        source_data={},
    )


def _show_item(*, source_item_id: str = "show-1") -> JellyfinCollectionItem:
    return JellyfinCollectionItem(
        source_item_id=source_item_id,
        item_type="show",
        library_id="tv",
        library_name="TV Shows",
        title="The X-Files",
        year=1993,
        tmdb_id=None,
        imdb_id=None,
        tvdb_id=77398,
        season_number=None,
        episode_number=None,
        show_source_item_id=None,
        show_title=None,
        show_year=None,
        show_tmdb_id=None,
        show_imdb_id=None,
        show_tvdb_id=None,
        added_at=None,
        runtime_seconds=None,
        file_path=None,
        source_data={},
    )


def _episode_item(*, source_item_id: str = "episode-1", season_number: int | None = 1) -> JellyfinCollectionItem:
    return JellyfinCollectionItem(
        source_item_id=source_item_id,
        item_type="episode",
        library_id="tv",
        library_name="TV Shows",
        title="Pilot",
        year=1993,
        tmdb_id=None,
        imdb_id=None,
        tvdb_id=None,
        season_number=season_number,
        episode_number=1,
        show_source_item_id="show-1",
        show_title="The X-Files",
        show_year=1993,
        show_tmdb_id=None,
        show_imdb_id=None,
        show_tvdb_id=77398,
        added_at=None,
        runtime_seconds=2800,
        file_path="D:/media/X-Files/S01E01.mkv",
        source_data={},
    )


def test_run_import_dry_run_counts_new_rows_and_missing_entries(monkeypatch) -> None:
    client = DummyClient(
        libraries=[
            JellyfinLibrary("movies", "Movies", "movies"),
            JellyfinLibrary("tv", "TV Shows", "tvshows"),
        ],
        items_by_library={
            "movies": [_movie_item()],
            "tv": [_show_item(), _episode_item()],
        },
    )
    session_obj = DummySession()

    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.find_collection_entry_by_source_item",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.count_entries_to_mark_missing",
        lambda *_args, **_kwargs: 2,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.show_repository.find_show_by_external_ids",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.show_repository.find_shows_by_title_and_year",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_external_ids",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_items_by_title_and_year",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_episode_media_item_by_show_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_episode_media_item",
        lambda *_args, **_kwargs: None,
    )

    result = JellyfinCollectionImportService.run_import(
        session_obj,
        payload=JellyfinCollectionImportRequest(dry_run=True),
        client=client,
    )

    assert result.status == "dry_run"
    assert result.processed_count == 3
    assert result.inserted_count == 3
    assert result.updated_count == 0
    assert result.missing_marked_count == 2
    assert result.media_items_created == 2
    assert result.shows_created == 1
    assert result.collection_entries_created == 3


def test_run_import_updates_existing_rows_and_marks_missing(monkeypatch) -> None:
    movie_media_item = SimpleNamespace(media_item_id=uuid4())
    existing_entry = SimpleNamespace(media_item_id=movie_media_item.media_item_id, show_id=None)
    batch_id = uuid4()
    client = DummyClient(
        libraries=[JellyfinLibrary("movies", "Movies", "movies")],
        items_by_library={"movies": [_movie_item()]},
    )
    session_obj = DummySession()
    finish_calls: dict[str, object] = {}

    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.find_collection_entry_by_source_item",
        lambda *_args, **_kwargs: existing_entry,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.get_media_item",
        lambda *_args, **_kwargs: movie_media_item,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.update_media_item",
        lambda *_args, **_kwargs: movie_media_item,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_tmdb_id",
        lambda *_args, **_kwargs: movie_media_item,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_imdb_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_tvdb_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.MediaItemService.determine_initial_enrichment_state",
        lambda **_kwargs: SimpleNamespace(status="pending", error=None),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.update_collection_entry",
        lambda *_args, **_kwargs: existing_entry,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.mark_missing_entries",
        lambda *_args, **_kwargs: 1,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.finish_import_batch",
        lambda *_args, **kwargs: finish_calls.update(kwargs),
    )

    result = JellyfinCollectionImportService.run_import(
        session_obj,
        payload=JellyfinCollectionImportRequest(dry_run=False),
        client=client,
    )

    assert result.status == "completed"
    assert result.updated_count == 1
    assert result.inserted_count == 0
    assert result.missing_marked_count == 1
    assert finish_calls["status"] == "completed"


def test_run_import_logs_ambiguous_title_match_and_creates_new_movie(monkeypatch) -> None:
    movie_media_item = SimpleNamespace(media_item_id=uuid4())
    batch_id = uuid4()
    client = DummyClient(
        libraries=[JellyfinLibrary("movies", "Movies", "movies")],
        items_by_library={"movies": [_movie_item(source_item_id="movie-ambiguous")]},
    )
    session_obj = DummySession()
    recorded_errors: list[dict] = []

    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.find_collection_entry_by_source_item",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_external_ids",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_items_by_title_and_year",
        lambda *_args, **_kwargs: [object(), object()],
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.create_media_item",
        lambda *_args, **_kwargs: movie_media_item,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_tmdb_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_imdb_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_tvdb_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.create_collection_entry",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.mark_missing_entries",
        lambda *_args, **_kwargs: 0,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.MediaItemService.determine_initial_enrichment_state",
        lambda **_kwargs: SimpleNamespace(status="pending", error=None),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.add_import_batch_error",
        lambda *_args, **kwargs: recorded_errors.append(kwargs),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.import_batch_repository.get_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id, errors_count=0),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.import_batch_repository.create_import_batch_error",
        lambda *_args, **kwargs: recorded_errors.append(kwargs),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.finish_import_batch",
        lambda *_args, **_kwargs: None,
    )

    result = JellyfinCollectionImportService.run_import(
        session_obj,
        payload=JellyfinCollectionImportRequest(dry_run=False),
        client=client,
    )

    assert result.inserted_count == 1
    assert result.media_items_created == 1
    assert recorded_errors[0]["severity"] == "warning"


def test_run_import_skips_invalid_episode_rows(monkeypatch) -> None:
    batch_id = uuid4()
    client = DummyClient(
        libraries=[JellyfinLibrary("tv", "TV Shows", "tvshows")],
        items_by_library={"tv": [_episode_item(season_number=None)]},
    )
    session_obj = DummySession()
    recorded_errors: list[dict] = []

    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.add_import_batch_error",
        lambda *_args, **kwargs: recorded_errors.append(kwargs),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.find_collection_entry_by_source_item",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.mark_missing_entries",
        lambda *_args, **_kwargs: 0,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.finish_import_batch",
        lambda *_args, **_kwargs: None,
    )

    result = JellyfinCollectionImportService.run_import(
        session_obj,
        payload=JellyfinCollectionImportRequest(dry_run=False),
        client=client,
    )

    assert result.error_count == 1
    assert result.skipped_count == 1
    assert recorded_errors[0]["entity_ref"] == "episode-1"


def test_run_import_item_errors_do_not_rollback_successful_outer_work(monkeypatch) -> None:
    batch_id = uuid4()
    created_entries: list[str] = []
    client = DummyClient(
        libraries=[JellyfinLibrary("movies", "Movies", "movies")],
        items_by_library={"movies": [_movie_item(source_item_id="movie-ok"), _movie_item(source_item_id="movie-bad")]},
    )
    session_obj = DummySession()

    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.find_collection_entry_by_source_item",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_external_ids",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_items_by_title_and_year",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_tmdb_id",
        lambda *_args, **kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_imdb_id",
        lambda *_args, **kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.find_media_item_by_tvdb_id",
        lambda *_args, **kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.MediaItemService.determine_initial_enrichment_state",
        lambda **_kwargs: SimpleNamespace(status="pending", error=None),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: SimpleNamespace(import_batch_id=batch_id),
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.finish_import_batch",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.ImportBatchService.add_import_batch_error",
        lambda *_args, **_kwargs: None,
    )

    def fake_create_media_item(_session, **kwargs):
        if kwargs["jellyfin_item_id"] == "movie-bad":
            raise ValueError("duplicate id conflict")
        return SimpleNamespace(media_item_id=uuid4())

    def fake_create_collection_entry(_session, **kwargs):
        created_entries.append(kwargs["source_item_id"])
        return None

    monkeypatch.setattr(
        "app.services.collection_imports.media_item_repository.create_media_item",
        fake_create_media_item,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.create_collection_entry",
        fake_create_collection_entry,
    )
    monkeypatch.setattr(
        "app.services.collection_imports.collection_repository.mark_missing_entries",
        lambda *_args, **_kwargs: 0,
    )

    result = JellyfinCollectionImportService.run_import(
        session_obj,
        payload=JellyfinCollectionImportRequest(dry_run=False),
        client=client,
    )

    assert result.inserted_count == 1
    assert result.error_count == 1
    assert created_entries == ["movie-ok"]
    assert session_obj.rollback_calls == 0
