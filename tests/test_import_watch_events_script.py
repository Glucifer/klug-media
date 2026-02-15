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
        "type": "movie",
        "watched_at": "2025-01-01T00:00:00Z",
        "player": "jellyfin",
        "tmdb_id": "100",
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
    rows = [_backup_row_dict()]
    input_path = tmp_path / "backup.json"
    report_path = tmp_path / "reports" / "errors.json"
    input_path.write_text(json.dumps(rows), encoding="utf-8")

    class DummySession:
        def close(self) -> None:
            return None

    monkeypatch.setattr(import_watch_events, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        import_watch_events.MediaItemService,
        "find_media_item_by_external_ids",
        lambda *_args, **_kwargs: None,
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

    assert exit_code == 2
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["rejected_count"] == 1


def test_run_returns_2_for_missing_file() -> None:
    exit_code = import_watch_events.run(["--input", "missing.json"])
    assert exit_code == 2
