from pathlib import Path
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
