from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from app.db.session import SessionLocal
from app.schemas.horrorfest_import import HorrorfestPreserveRow
from app.services.horrorfest_import import HorrorfestImportService


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import preserved Horrorfest overlay data onto existing watch history."
    )
    parser.add_argument("--input", required=True, help="Path to Horrorfest preserve CSV")
    parser.add_argument("--user-id", required=True, help="Klug user UUID")
    parser.add_argument(
        "--updated-by",
        default="import",
        help="Operator label stored on updated rows",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and summarize without writing to the database",
    )
    parser.add_argument(
        "--error-report",
        default=None,
        help="Optional path to write unmatched rows as JSON",
    )
    return parser.parse_args(argv)


def _load_csv_rows(file_path: Path) -> list[dict[str, Any]]:
    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [{key: value for key, value in row.items() if key is not None} for row in reader]


def _write_error_report(path: Path, unmatched_rows: list[dict[str, Any]]) -> None:
    payload = {
        "unmatched_count": len(unmatched_rows),
        "rows": unmatched_rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 2

    try:
        user_id = UUID(args.user_id)
        raw_rows = _load_csv_rows(input_path)
        rows = [HorrorfestPreserveRow.model_validate(row) for row in raw_rows]
    except (ValueError, ValidationError) as exc:
        print(f"Input validation failed: {exc}")
        return 2

    session = SessionLocal()
    try:
        result = HorrorfestImportService.run_preserve_import(
            session,
            user_id=user_id,
            rows=rows,
            dry_run=args.dry_run,
            updated_by=args.updated_by,
        )
    except Exception as exc:
        session.rollback()
        print(f"Horrorfest import failed: {exc}")
        return 1
    finally:
        session.close()

    print("Horrorfest import summary")
    print(f"  processed: {result.processed_count}")
    print(f"  matched: {result.matched_count}")
    print(f"  updated: {result.updated_count}")
    print(f"  errors: {result.error_count}")
    print(f"  year_configs_created: {result.year_configs_created}")
    print(f"  dry_run: {args.dry_run}")
    if result.unmatched_rows:
        print("  unmatched sample:")
        for row in result.unmatched_rows[:10]:
            print(
                "   - "
                f"trakt_log_id={row['trakt_log_id']} "
                f"tmdb_id={row['tmdb_id']} "
                f"watched_at={row['watched_at']} "
                f"watch_year={row['watch_year']} "
                f"watch_order={row['watch_order']}"
            )
    if args.error_report and result.unmatched_rows:
        report_path = Path(args.error_report)
        _write_error_report(report_path, result.unmatched_rows)
        print(f"  wrote_error_report: {report_path}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
