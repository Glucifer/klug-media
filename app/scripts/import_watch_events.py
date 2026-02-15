from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.db.session import SessionLocal
from app.schemas.imports import ImportMode, LegacySourceWatchEventImportRequest
from app.services.imports import WatchEventImportService


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import watch events from a legacy source export file."
    )
    parser.add_argument(
        "--input", required=True, help="Path to JSON or CSV export file"
    )
    parser.add_argument(
        "--format",
        choices=["auto", "json", "csv"],
        default="auto",
        help="Input format detection mode",
    )
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in ImportMode],
        default=ImportMode.bootstrap.value,
        help="Import mode",
    )
    parser.add_argument(
        "--source-detail", default=None, help="Optional source detail label"
    )
    parser.add_argument("--notes", default=None, help="Optional import notes")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and summarize without writing to the database",
    )
    parser.add_argument(
        "--resume-from-latest",
        action="store_true",
        help="For incremental mode, resume from latest stored cursor",
    )
    return parser.parse_args(argv)


def _detect_format(file_path: Path, explicit_format: str) -> str:
    if explicit_format in {"json", "csv"}:
        return explicit_format

    suffix = file_path.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"

    raise ValueError(
        "Could not detect format from file extension. Use --format json or --format csv."
    )


def _load_json_rows(file_path: Path) -> list[dict[str, Any]]:
    with file_path.open("r", encoding="utf-8") as file:
        parsed = json.load(file)

    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict) and isinstance(parsed.get("rows"), list):
        return parsed["rows"]

    raise ValueError(
        "JSON input must be a list of row objects or an object with a 'rows' list"
    )


def _load_csv_rows(file_path: Path) -> list[dict[str, Any]]:
    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows: list[dict[str, Any]] = []
        for row in reader:
            cleaned = {key: value for key, value in row.items() if key is not None}
            rows.append(cleaned)
        return rows


def _load_rows(file_path: Path, file_format: str) -> list[dict[str, Any]]:
    if file_format == "json":
        return _load_json_rows(file_path)
    if file_format == "csv":
        return _load_csv_rows(file_path)
    raise ValueError(f"Unsupported format: {file_format}")


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 2

    try:
        detected_format = _detect_format(input_path, args.format)
        rows = _load_rows(input_path, detected_format)
        payload = LegacySourceWatchEventImportRequest(
            mode=ImportMode(args.mode),
            dry_run=args.dry_run,
            resume_from_latest=args.resume_from_latest,
            source_detail=args.source_detail,
            notes=args.notes,
            rows=rows,
        )
    except (ValueError, ValidationError, json.JSONDecodeError) as exc:
        print(f"Input validation failed: {exc}")
        return 2

    session = SessionLocal()
    try:
        result = WatchEventImportService.run_legacy_source_import(
            session, payload=payload
        )
    except Exception as exc:
        print(f"Import failed: {exc}")
        return 1
    finally:
        session.close()

    print("Import summary")
    print(f"  batch_id: {result.import_batch_id}")
    print(f"  status: {result.status}")
    print(f"  dry_run: {result.dry_run}")
    print(f"  processed: {result.processed_count}")
    print(f"  inserted: {result.inserted_count}")
    print(f"  skipped: {result.skipped_count}")
    print(f"  errors: {result.error_count}")
    print(f"  cursor_before: {result.cursor_before}")
    print(f"  cursor_after: {result.cursor_after}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
