from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from app.scripts import import_watch_events
from app.services.imports import WatchEventImportResult


def _row_dict() -> dict[str, str]:
    return {
        "user_id": str(uuid4()),
        "media_item_id": str(uuid4()),
        "watched_at": "2025-01-01T00:00:00Z",
        "player": "jellyfin",
        "completed": "true",
    }


def _backup_row_dict() -> dict[str, str]:
    return {
        "id": "legacy-evt-1",
        "type": "episode",
        "watched_at": "2025-01-01T00:00:00Z",
        "player": "jellyfin",
        "episode": {
            "season": 1,
            "number": 8,
            "title": "The Nest",
            "ids": {"tmdb": 4765221, "imdb": "tt28634845", "tvdb": 10081853},
        },
        "show": {
            "title": "Scavengers Reign",
            "year": 2023,
            "ids": {"tmdb": 204154},
        },
    }


def test_load_json_rows_from_array(tmp_path: Path) -> None:
    rows = [_row_dict()]
    file_path = tmp_path / "events.json"
    file_path.write_text(json.dumps(rows), encoding="utf-8")

    loaded = import_watch_events._load_json_rows(file_path)

    assert loaded == rows


def test_load_json_rows_from_object_wrapper(tmp_path: Path) -> None:
    rows = [_row_dict()]
    file_path = tmp_path / "events.json"
    file_path.write_text(json.dumps({"rows": rows}), encoding="utf-8")

    loaded = import_watch_events._load_json_rows(file_path)

    assert loaded == rows


def test_load_csv_rows(tmp_path: Path) -> None:
    row = _row_dict()
    file_path = tmp_path / "events.csv"
    file_path.write_text(
        "user_id,media_item_id,watched_at,player,completed\n"
        f"{row['user_id']},{row['media_item_id']},{row['watched_at']},{row['player']},{row['completed']}\n",
        encoding="utf-8",
    )

    loaded = import_watch_events._load_csv_rows(file_path)

    assert len(loaded) == 1
    assert loaded[0]["player"] == "jellyfin"


def test_run_executes_import_service(monkeypatch, tmp_path: Path) -> None:
    rows = [_row_dict()]
    input_path = tmp_path / "events.json"
    input_path.write_text(json.dumps(rows), encoding="utf-8")

    class DummySession:
        def close(self) -> None:
            return None

    expected_result = WatchEventImportResult(
        import_batch_id=uuid4(),
        status="dry_run",
        dry_run=True,
        processed_count=1,
        inserted_count=1,
        skipped_count=0,
        error_count=0,
    )

    monkeypatch.setattr(import_watch_events, "SessionLocal", lambda: DummySession())

    def fake_run_legacy_source_import(session, *, payload):
        assert payload.dry_run is True
        assert payload.resume_from_latest is True
        assert payload.rejected_before_import == 0
        assert len(payload.rows) == 1
        assert session is not None
        return expected_result

    monkeypatch.setattr(
        import_watch_events.WatchEventImportService,
        "run_legacy_source_import",
        fake_run_legacy_source_import,
    )

    exit_code = import_watch_events.run(
        [
            "--input",
            str(input_path),
            "--input-schema",
            "mapped_rows",
            "--mode",
            "incremental",
            "--dry-run",
            "--resume-from-latest",
        ]
    )

    assert exit_code == 0


def test_run_legacy_backup_writes_error_report(monkeypatch, tmp_path: Path) -> None:
    rows = [_backup_row_dict()]
    input_path = tmp_path / "backup.json"
    report_path = tmp_path / "reports" / "errors.json"
    input_path.write_text(json.dumps(rows), encoding="utf-8")

    class DummySession:
        def close(self) -> None:
            return None

    class DummyMediaItem:
        def __init__(self) -> None:
            self.media_item_id = uuid4()

    expected_result = WatchEventImportResult(
        import_batch_id=uuid4(),
        status="completed",
        dry_run=False,
        processed_count=1,
        inserted_count=1,
        skipped_count=0,
        error_count=0,
    )

    monkeypatch.setattr(import_watch_events, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        import_watch_events.MediaItemService,
        "find_media_item_by_external_ids",
        lambda *_args, **_kwargs: DummyMediaItem(),
    )
    monkeypatch.setattr(
        import_watch_events.WatchEventImportService,
        "run_legacy_source_import",
        lambda _session, *, payload: (
            expected_result
            if payload.rejected_before_import == 0
            else (_ for _ in ()).throw(AssertionError("unexpected rejected count"))
        ),
    )

    exit_code = import_watch_events.run(
        [
            "--input",
            str(input_path),
            "--input-schema",
            "legacy_backup",
            "--user-id",
            str(uuid4()),
            "--error-report",
            str(report_path),
        ]
    )

    assert exit_code == 0
    assert not report_path.exists()


def test_run_legacy_backup_rejected_rows_write_report(
    monkeypatch, tmp_path: Path
) -> None:
    rows = [{"id": "legacy-evt-1", "type": "movie"}]
    input_path = tmp_path / "backup.json"
    report_path = tmp_path / "reports" / "errors.json"
    input_path.write_text(json.dumps(rows), encoding="utf-8")

    class DummySession:
        def close(self) -> None:
            return None

    monkeypatch.setattr(import_watch_events, "SessionLocal", lambda: DummySession())
    exit_code = import_watch_events.run(
        [
            "--input",
            str(input_path),
            "--input-schema",
            "legacy_backup",
            "--user-id",
            str(uuid4()),
            "--error-report",
            str(report_path),
        ]
    )

    assert exit_code == 2
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["rejected_count"] == 1


def test_legacy_backup_creates_missing_media_item(monkeypatch) -> None:
    class DummyShow:
        def __init__(self) -> None:
            self.show_id = uuid4()

    class DummySession:
        def __init__(self) -> None:
            self.created = 0
            self.commits = 0
            self.last_media_item = None

        def add(self, media_item) -> None:
            media_item.media_item_id = uuid4()
            self.last_media_item = media_item
            self.created += 1

        def flush(self) -> None:
            return None

        def commit(self) -> None:
            self.commits += 1

        def close(self) -> None:
            return None

    dummy_session = DummySession()
    monkeypatch.setattr(import_watch_events, "SessionLocal", lambda: dummy_session)
    monkeypatch.setattr(
        import_watch_events.MediaItemService,
        "find_media_item_by_external_ids",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        import_watch_events.ShowService,
        "get_or_create_show",
        lambda *_args, **_kwargs: DummyShow(),
    )

    mapped_rows, rejected_rows = import_watch_events._build_mapped_rows_from_legacy_backup(
        [_backup_row_dict()],
        user_id=uuid4(),
    )

    assert not rejected_rows
    assert len(mapped_rows) == 1
    assert dummy_session.created == 1
    assert dummy_session.commits == 1
    assert dummy_session.last_media_item is not None
    assert dummy_session.last_media_item.show_tmdb_id == 204154
    assert dummy_session.last_media_item.season_number == 1
    assert dummy_session.last_media_item.episode_number == 8
    assert dummy_session.last_media_item.show_id is not None


def test_run_returns_2_for_missing_file() -> None:
    exit_code = import_watch_events.run(["--input", "missing.json"])
    assert exit_code == 2
