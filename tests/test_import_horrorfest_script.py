from pathlib import Path
import json
from uuid import uuid4

from app.scripts import import_horrorfest
from app.schemas.horrorfest_import import HorrorfestPreserveImportSummary


def test_run_horrorfest_import_executes_service(monkeypatch, tmp_path: Path) -> None:
    input_path = tmp_path / "horrorfest.csv"
    input_path.write_text(
        "\n".join(
            [
                "trakt_log_id,watched_at,rewatch,watch_order,alternate_version,watch_rating,watch_year,movie_id,tmdb_id,origin_country,original_language,runtime_used",
                "9352788816,2012-10-01,1,1,std,10,2012,1317,2654,US,en,95",
            ]
        ),
        encoding="utf-8",
    )

    class DummySession:
        def rollback(self) -> None:
            return None

        def close(self) -> None:
            return None

    monkeypatch.setattr(import_horrorfest, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        import_horrorfest.HorrorfestImportService,
        "run_preserve_import",
        lambda _session, **_kwargs: HorrorfestPreserveImportSummary(
            processed_count=1,
            matched_count=1,
            updated_count=1,
            error_count=0,
            year_configs_created=1,
            unmatched_rows=[],
        ),
    )

    exit_code = import_horrorfest.run(
        [
            "--input",
            str(input_path),
            "--user-id",
            str(uuid4()),
            "--dry-run",
        ]
    )

    assert exit_code == 0


def test_run_horrorfest_import_returns_2_for_missing_file() -> None:
    exit_code = import_horrorfest.run(
        ["--input", "missing.csv", "--user-id", str(uuid4())]
    )
    assert exit_code == 2


def test_run_horrorfest_import_writes_unmatched_report(monkeypatch, tmp_path: Path) -> None:
    input_path = tmp_path / "horrorfest.csv"
    report_path = tmp_path / "reports" / "unmatched.json"
    input_path.write_text(
        "\n".join(
            [
                "trakt_log_id,watched_at,rewatch,watch_order,alternate_version,watch_rating,watch_year,movie_id,tmdb_id,origin_country,original_language,runtime_used",
                "9352788816,2012-10-01,1,1,std,10,2012,1317,2654,US,en,95",
            ]
        ),
        encoding="utf-8",
    )

    class DummySession:
        def rollback(self) -> None:
            return None

        def close(self) -> None:
            return None

    monkeypatch.setattr(import_horrorfest, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        import_horrorfest.HorrorfestImportService,
        "run_preserve_import",
        lambda _session, **_kwargs: HorrorfestPreserveImportSummary(
            processed_count=1,
            matched_count=0,
            updated_count=0,
            error_count=1,
            year_configs_created=0,
            unmatched_rows=[
                {
                    "trakt_log_id": "9352788816",
                    "tmdb_id": 2654,
                    "watched_at": "2012-10-01",
                    "watch_year": 2012,
                    "watch_order": 1,
                    "alternate_version": "std",
                }
            ],
        ),
    )

    exit_code = import_horrorfest.run(
        [
            "--input",
            str(input_path),
            "--user-id",
            str(uuid4()),
            "--dry-run",
            "--error-report",
            str(report_path),
        ]
    )

    assert exit_code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["unmatched_count"] == 1
