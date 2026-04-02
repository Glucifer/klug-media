from uuid import uuid4
from unittest.mock import Mock

from app.schemas.horrorfest_import import HorrorfestPreserveRow
from app.services.horrorfest_import import HorrorfestImportService


def _row(**overrides) -> HorrorfestPreserveRow:
    payload = {
        "trakt_log_id": "9352788816",
        "watched_at": "2012-10-01",
        "rewatch": True,
        "watch_order": 1,
        "alternate_version": "std",
        "watch_rating": 10,
        "watch_year": 2012,
        "movie_id": 1317,
        "tmdb_id": 2654,
        "origin_country": "US",
        "original_language": "en",
        "runtime_used": 95,
    }
    payload.update(overrides)
    return HorrorfestPreserveRow.model_validate(payload)


def test_run_preserve_import_matches_by_source_event_id(monkeypatch) -> None:
    session = Mock()
    watch_event = Mock(watch_id=uuid4())

    monkeypatch.setattr(
        "app.services.horrorfest_import.HorrorfestService.list_years",
        lambda *_args, **_kwargs: [{"horrorfest_year": 2012}],
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.find_user_watch_event_by_source_event_id",
        lambda *_args, **_kwargs: watch_event,
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_tmdb_and_local_date",
        lambda *_args, **_kwargs: [],
    )
    apply_mock = Mock(return_value=True)
    monkeypatch.setattr(
        HorrorfestImportService,
        "_apply_preserved_horrorfest_metadata",
        apply_mock,
    )

    result = HorrorfestImportService.run_preserve_import(
        session,
        user_id=uuid4(),
        rows=[_row()],
        dry_run=False,
        updated_by="import",
    )

    assert result.processed_count == 1
    assert result.matched_count == 1
    assert result.updated_count == 1
    assert result.error_count == 0
    apply_mock.assert_called_once()


def test_run_preserve_import_falls_back_to_tmdb_and_local_date(monkeypatch) -> None:
    session = Mock()
    watch_event = Mock(watch_id=uuid4())

    monkeypatch.setattr(
        "app.services.horrorfest_import.HorrorfestService.list_years",
        lambda *_args, **_kwargs: [{"horrorfest_year": 2012}],
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.find_user_watch_event_by_source_event_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_tmdb_and_local_date",
        lambda *_args, **_kwargs: [watch_event],
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_local_year",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        HorrorfestImportService,
        "_apply_preserved_horrorfest_metadata",
        lambda *_args, **_kwargs: True,
    )

    result = HorrorfestImportService.run_preserve_import(
        session,
        user_id=uuid4(),
        rows=[_row()],
        dry_run=False,
        updated_by="import",
    )

    assert result.matched_count == 1
    assert result.error_count == 0


def test_run_preserve_import_falls_back_to_nearby_local_date(monkeypatch) -> None:
    session = Mock()
    watch_event = Mock(watch_id=uuid4())

    monkeypatch.setattr(
        "app.services.horrorfest_import.HorrorfestService.list_years",
        lambda *_args, **_kwargs: [{"horrorfest_year": 2012}],
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.find_user_watch_event_by_source_event_id",
        lambda *_args, **_kwargs: None,
    )

    def fake_by_date(_session, *, local_date, **_kwargs):
        if str(local_date) == "2012-10-02":
            return [watch_event]
        return []

    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_tmdb_and_local_date",
        fake_by_date,
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_local_year",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        HorrorfestImportService,
        "_apply_preserved_horrorfest_metadata",
        lambda *_args, **_kwargs: True,
    )

    result = HorrorfestImportService.run_preserve_import(
        session,
        user_id=uuid4(),
        rows=[_row(watched_at="2012-10-01")],
        dry_run=False,
        updated_by="import",
    )

    assert result.matched_count == 1
    assert result.error_count == 0


def test_run_preserve_import_falls_back_to_year_watch_order(monkeypatch) -> None:
    session = Mock()
    matching_watch = Mock(watch_id=uuid4())
    matching_watch.media_item = Mock(tmdb_id=2654)
    other_watch = Mock(watch_id=uuid4())
    other_watch.media_item = Mock(tmdb_id=9999)

    monkeypatch.setattr(
        "app.services.horrorfest_import.HorrorfestService.list_years",
        lambda *_args, **_kwargs: [{"horrorfest_year": 2012}],
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.find_user_watch_event_by_source_event_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_tmdb_and_local_date",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_local_year",
        lambda *_args, **_kwargs: [other_watch, matching_watch],
    )
    monkeypatch.setattr(
        HorrorfestImportService,
        "_apply_preserved_horrorfest_metadata",
        lambda *_args, **_kwargs: True,
    )

    result = HorrorfestImportService.run_preserve_import(
        session,
        user_id=uuid4(),
        rows=[_row(watch_order=2)],
        dry_run=False,
        updated_by="import",
    )

    assert result.matched_count == 1
    assert result.error_count == 0


def test_run_preserve_import_creates_missing_year_configs_in_dry_run(monkeypatch) -> None:
    session = Mock()

    monkeypatch.setattr(
        "app.services.horrorfest_import.HorrorfestService.list_years",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.find_user_watch_event_by_source_event_id",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_tmdb_and_local_date",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        "app.services.horrorfest_import.watch_event_repository.list_user_movie_watch_events_by_local_year",
        lambda *_args, **_kwargs: [],
    )

    result = HorrorfestImportService.run_preserve_import(
        session,
        user_id=uuid4(),
        rows=[_row(), _row(trakt_log_id="2", watch_order=2, watched_at="2012-10-02")],
        dry_run=True,
        updated_by="import",
    )

    assert result.year_configs_created == 1
    assert result.error_count == 2


def test_map_version_override_handles_alt_and_std() -> None:
    assert HorrorfestImportService._map_version_override(_row(alternate_version="std")) == (
        None,
        None,
    )
    assert HorrorfestImportService._map_version_override(
        _row(alternate_version="alt", runtime_used=101)
    ) == ("Alternate Cut", 101)


def test_preserve_row_allows_multi_country_legacy_values() -> None:
    row = _row(origin_country="BE,FR,GB,US", original_language="en,fr")

    assert row.origin_country == "BE,FR,GB,US"
    assert row.original_language == "en,fr"
