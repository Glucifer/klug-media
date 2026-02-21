from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.db.models.entities import MediaItem
from app.db.session import SessionLocal
from app.schemas.imports import ImportMode, LegacySourceWatchEventImportRequest
from app.services.imports import WatchEventImportService
from app.services.media_items import MediaItemService
from app.services.shows import ShowService


@dataclass(frozen=True)
class LegacyBackupPreprocessResult:
    mapped_rows: list[dict[str, Any]]
    rejected_rows: list[dict[str, Any]]
    media_items_created: int
    shows_created: int


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
        "--input-schema",
        choices=["mapped_rows", "legacy_backup"],
        default="legacy_backup",
        help="Schema of the input rows",
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
        "--user-id",
        default=None,
        help="Required for legacy_backup schema; UUID of internal user",
    )
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
    parser.add_argument(
        "--error-report",
        default=None,
        help="Optional path to write rejected rows as JSON",
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

    if isinstance(parsed, dict):
        for key in ("rows", "watched", "history"):
            value = parsed.get(key)
            if isinstance(value, list):
                return value

    raise ValueError(
        "JSON input must be a list of row objects, or object containing one of: rows/watched/history"
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


def _parse_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    try:
        return int(str(value))
    except ValueError:
        return None


def _parse_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _parse_bool(value: Any, *, default: bool) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "t", "yes", "y"}:
        return True
    if normalized in {"0", "false", "f", "no", "n"}:
        return False
    return default


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value

    text_value = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text_value)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _extract_media_type(row: dict[str, Any]) -> str | None:
    direct = row.get("type") or row.get("media_type")
    if isinstance(direct, str) and direct.strip():
        normalized = direct.strip().lower()
        if normalized in {"movie", "episode", "show"}:
            return normalized

    if isinstance(row.get("movie"), dict):
        return "movie"
    if isinstance(row.get("episode"), dict):
        return "episode"
    if isinstance(row.get("show"), dict):
        return "show"
    return None


def _extract_nested_ids(container: Any) -> tuple[int | None, str | None]:
    if not isinstance(container, dict):
        return None, None
    ids = container.get("ids") if isinstance(container.get("ids"), dict) else container
    tmdb_id = _parse_int(ids.get("tmdb")) if isinstance(ids, dict) else None
    imdb_id = ids.get("imdb") if isinstance(ids, dict) else None
    if isinstance(imdb_id, str):
        imdb_id = imdb_id.strip() or None
    else:
        imdb_id = None
    return tmdb_id, imdb_id


def _extract_external_ids(
    row: dict[str, Any], media_type: str
) -> tuple[int | None, str | None]:
    top_tmdb = _parse_int(row.get("tmdb_id"))
    top_imdb = row.get("imdb_id")
    if isinstance(top_imdb, str):
        top_imdb = top_imdb.strip() or None
    else:
        top_imdb = None

    if top_tmdb is not None or top_imdb is not None:
        return top_tmdb, top_imdb

    nested_target = row.get(media_type)
    nested_tmdb, nested_imdb = _extract_nested_ids(nested_target)
    if nested_tmdb is not None or nested_imdb is not None:
        return nested_tmdb, nested_imdb

    return _extract_nested_ids(row)


def _extract_media_title(row: dict[str, Any], media_type: str) -> str | None:
    title_value = row.get("title")
    if isinstance(title_value, str) and title_value.strip():
        return title_value.strip()

    nested = row.get(media_type)
    if isinstance(nested, dict):
        nested_title = nested.get("title")
        if isinstance(nested_title, str) and nested_title.strip():
            return nested_title.strip()

    show_value = row.get("show")
    if isinstance(show_value, dict):
        show_title = show_value.get("title")
        if isinstance(show_title, str) and show_title.strip():
            return show_title.strip()

    return None


def _extract_media_year(row: dict[str, Any], media_type: str) -> int | None:
    year_value = _parse_int(row.get("year"))
    if year_value is not None:
        return year_value

    nested = row.get(media_type)
    if isinstance(nested, dict):
        nested_year = _parse_int(nested.get("year"))
        if nested_year is not None:
            return nested_year

    show_value = row.get("show")
    if isinstance(show_value, dict):
        return _parse_int(show_value.get("year"))

    return None


def _extract_tvdb_id(row: dict[str, Any], media_type: str) -> int | None:
    top_tvdb = _parse_int(row.get("tvdb_id"))
    if top_tvdb is not None:
        return top_tvdb

    nested = row.get(media_type)
    if isinstance(nested, dict):
        ids = nested.get("ids")
        if isinstance(ids, dict):
            return _parse_int(ids.get("tvdb"))

    return None


def _extract_show_tmdb_id(row: dict[str, Any], media_type: str) -> int | None:
    top_show_tmdb = _parse_int(row.get("show_tmdb_id"))
    if top_show_tmdb is not None:
        return top_show_tmdb

    if media_type != "episode":
        return None

    show_value = row.get("show")
    if isinstance(show_value, dict):
        ids = show_value.get("ids")
        if isinstance(ids, dict):
            return _parse_int(ids.get("tmdb"))

    return None


def _extract_show_tvdb_id(row: dict[str, Any], media_type: str) -> int | None:
    top_show_tvdb = _parse_int(row.get("show_tvdb_id"))
    if top_show_tvdb is not None:
        return top_show_tvdb

    if media_type != "episode":
        return None

    show_value = row.get("show")
    if isinstance(show_value, dict):
        ids = show_value.get("ids")
        if isinstance(ids, dict):
            return _parse_int(ids.get("tvdb"))

    return None


def _extract_show_imdb_id(row: dict[str, Any], media_type: str) -> str | None:
    top_show_imdb = row.get("show_imdb_id")
    if isinstance(top_show_imdb, str):
        normalized = top_show_imdb.strip()
        if normalized:
            return normalized

    if media_type != "episode":
        return None

    show_value = row.get("show")
    if isinstance(show_value, dict):
        ids = show_value.get("ids")
        if isinstance(ids, dict):
            show_imdb = ids.get("imdb")
            if isinstance(show_imdb, str):
                normalized = show_imdb.strip()
                if normalized:
                    return normalized

    return None


def _extract_show_title(row: dict[str, Any], media_type: str) -> str | None:
    top_show_title = row.get("show_title")
    if isinstance(top_show_title, str):
        normalized = top_show_title.strip()
        if normalized:
            return normalized

    if media_type != "episode":
        return None

    show_value = row.get("show")
    if isinstance(show_value, dict):
        show_title = show_value.get("title")
        if isinstance(show_title, str):
            normalized = show_title.strip()
            if normalized:
                return normalized

    return None


def _extract_show_year(row: dict[str, Any], media_type: str) -> int | None:
    top_show_year = _parse_int(row.get("show_year"))
    if top_show_year is not None:
        return top_show_year

    if media_type != "episode":
        return None

    show_value = row.get("show")
    if isinstance(show_value, dict):
        return _parse_int(show_value.get("year"))

    return None


def _extract_season_episode_numbers(
    row: dict[str, Any], media_type: str
) -> tuple[int | None, int | None]:
    season_number = _parse_int(row.get("season_number"))
    episode_number = _parse_int(row.get("episode_number"))
    if season_number is not None or episode_number is not None:
        return season_number, episode_number

    if media_type != "episode":
        return None, None

    episode_value = row.get("episode")
    if isinstance(episode_value, dict):
        return (
            _parse_int(episode_value.get("season")),
            _parse_int(episode_value.get("number")),
        )

    return None, None


def _create_media_item_from_backup_row(
    session: Any,
    *,
    row: dict[str, Any],
    media_type: str,
    tmdb_id: int | None,
    imdb_id: str | None,
) -> tuple[MediaItem, bool]:
    title = _extract_media_title(row, media_type)
    if not title:
        fallback_id = tmdb_id or imdb_id or row.get("id") or "unknown"
        title = f"{media_type}:{fallback_id}"

    season_number, episode_number = _extract_season_episode_numbers(row, media_type)
    show_tmdb_id = _extract_show_tmdb_id(row, media_type)
    show_id: UUID | None = None
    show_created = False

    if media_type == "episode" and show_tmdb_id is not None:
        existing_show = ShowService.find_show_by_tmdb_id(session, tmdb_id=show_tmdb_id)
        show_title = _extract_show_title(row, media_type) or f"show:{show_tmdb_id}"
        show = ShowService.get_or_create_show(
            session,
            tmdb_id=show_tmdb_id,
            title=show_title,
            year=_extract_show_year(row, media_type),
            tvdb_id=_extract_show_tvdb_id(row, media_type),
            imdb_id=_extract_show_imdb_id(row, media_type),
        )
        show_id = show.show_id
        show_created = existing_show is None

    media_item = MediaItem(
        type=media_type,
        title=title,
        year=_extract_media_year(row, media_type),
        tmdb_id=tmdb_id,
        imdb_id=imdb_id,
        tvdb_id=_extract_tvdb_id(row, media_type),
        show_tmdb_id=show_tmdb_id,
        season_number=season_number,
        episode_number=episode_number,
        show_id=show_id,
        metadata_source="legacy_backup",
    )
    session.add(media_item)
    session.flush()
    return media_item, show_created


def _build_mapped_rows_from_legacy_backup(
    raw_rows: list[dict[str, Any]],
    *,
    user_id: UUID,
    dry_run: bool,
) -> LegacyBackupPreprocessResult:
    session = SessionLocal()
    mapped_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    created_media_items = 0
    created_shows = 0
    planned_shows: set[int] = set()
    planned_media_items: dict[tuple[str, int | str], UUID] = {}

    try:
        for index, row in enumerate(raw_rows):
            if not isinstance(row, dict):
                rejected_rows.append(
                    {"row_index": index, "reason": "row is not an object", "row": row}
                )
                continue

            watched_at = _parse_datetime(row.get("watched_at") or row.get("played_at"))
            if watched_at is None:
                rejected_rows.append(
                    {
                        "row_index": index,
                        "reason": "missing or invalid watched_at/played_at",
                        "row": row,
                    }
                )
                continue

            media_type = _extract_media_type(row)
            if media_type is None:
                rejected_rows.append(
                    {"row_index": index, "reason": "missing media type", "row": row}
                )
                continue

            tmdb_id, imdb_id = _extract_external_ids(row, media_type)
            media_item = MediaItemService.find_media_item_by_external_ids(
                session,
                media_type=media_type,
                tmdb_id=tmdb_id,
                imdb_id=imdb_id,
            )
            if media_item is None:
                media_key: tuple[str, int | str] | None = None
                if tmdb_id is not None:
                    media_key = (media_type, tmdb_id)
                elif imdb_id is not None:
                    media_key = (media_type, imdb_id)

                if dry_run:
                    if media_type == "episode":
                        show_tmdb_id = _extract_show_tmdb_id(row, media_type)
                        if show_tmdb_id is not None:
                            existing_show = ShowService.find_show_by_tmdb_id(
                                session, tmdb_id=show_tmdb_id
                            )
                            if (
                                existing_show is None
                                and show_tmdb_id not in planned_shows
                            ):
                                planned_shows.add(show_tmdb_id)
                                created_shows += 1

                    if media_key is not None:
                        planned_media_item_id = planned_media_items.get(media_key)
                        if planned_media_item_id is None:
                            planned_media_item_id = uuid4()
                            planned_media_items[media_key] = planned_media_item_id
                            created_media_items += 1
                        media_item_id = planned_media_item_id
                    else:
                        media_item_id = uuid4()
                        created_media_items += 1
                else:
                    try:
                        media_item, show_created = _create_media_item_from_backup_row(
                            session,
                            row=row,
                            media_type=media_type,
                            tmdb_id=tmdb_id,
                            imdb_id=imdb_id,
                        )
                        created_media_items += 1
                        if show_created:
                            created_shows += 1
                    except IntegrityError:
                        session.rollback()
                        media_item = MediaItemService.find_media_item_by_external_ids(
                            session,
                            media_type=media_type,
                            tmdb_id=tmdb_id,
                            imdb_id=imdb_id,
                        )
                        if media_item is None:
                            rejected_rows.append(
                                {
                                    "row_index": index,
                                    "reason": "no matching media_item for external ids",
                                    "row": row,
                                    "lookup": {
                                        "media_type": media_type,
                                        "tmdb_id": tmdb_id,
                                        "imdb_id": imdb_id,
                                    },
                                }
                            )
                            continue
                    media_item_id = media_item.media_item_id
            else:
                media_item_id = media_item.media_item_id

            source_event_id = row.get("source_event_id") or row.get("id")
            if source_event_id is not None:
                source_event_id = str(source_event_id)

            playback_source = (
                row.get("player") or row.get("playback_source") or "legacy_backup"
            )

            mapped_rows.append(
                {
                    "user_id": str(user_id),
                    "media_item_id": str(media_item_id),
                    "watched_at": watched_at.isoformat(),
                    "player": str(playback_source),
                    "total_seconds": _parse_int(row.get("total_seconds")),
                    "watched_seconds": _parse_int(row.get("watched_seconds")),
                    "progress_percent": _parse_decimal(
                        row.get("progress_percent") or row.get("progress")
                    ),
                    "completed": _parse_bool(row.get("completed"), default=True),
                    "rating": _parse_decimal(
                        row.get("rating") or row.get("rating_value")
                    ),
                    "media_version_id": row.get("media_version_id"),
                    "source_event_id": source_event_id,
                }
            )
        if created_media_items > 0 and not dry_run:
            session.commit()
    finally:
        session.close()

    return LegacyBackupPreprocessResult(
        mapped_rows=mapped_rows,
        rejected_rows=rejected_rows,
        media_items_created=created_media_items,
        shows_created=created_shows,
    )


def _write_error_report(path: Path, rows: list[dict[str, Any]]) -> None:
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "rejected_count": len(rows),
        "rows": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    input_path = Path(args.input)
    rejected_rows: list[dict[str, Any]] = []
    media_items_created = 0
    shows_created = 0

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 2

    try:
        detected_format = _detect_format(input_path, args.format)
        raw_rows = _load_rows(input_path, detected_format)

        rows_for_validation = raw_rows

        if args.input_schema == "legacy_backup":
            if args.user_id is None:
                raise ValueError(
                    "--user-id is required for --input-schema legacy_backup"
                )
            user_id = UUID(args.user_id)
            preprocess = _build_mapped_rows_from_legacy_backup(
                raw_rows,
                user_id=user_id,
                dry_run=args.dry_run,
            )
            rows_for_validation = preprocess.mapped_rows
            rejected_rows = preprocess.rejected_rows
            media_items_created = preprocess.media_items_created
            shows_created = preprocess.shows_created

        if not rows_for_validation:
            raise ValueError("No valid rows available for import")

        payload = LegacySourceWatchEventImportRequest(
            mode=ImportMode(args.mode),
            dry_run=args.dry_run,
            resume_from_latest=args.resume_from_latest,
            source_detail=args.source_detail,
            notes=args.notes,
            rejected_before_import=len(rejected_rows),
            media_items_created=media_items_created,
            shows_created=shows_created,
            rows=rows_for_validation,
        )
    except (ValueError, ValidationError, json.JSONDecodeError) as exc:
        if args.error_report and rejected_rows:
            report_path = Path(args.error_report)
            _write_error_report(report_path, rejected_rows)
            print(
                f"Wrote error report: {report_path} ({len(rejected_rows)} rejected rows)"
            )
        print(f"Input validation failed: {exc}")
        return 2

    if args.error_report and rejected_rows:
        report_path = Path(args.error_report)
        _write_error_report(report_path, rejected_rows)
        print(f"Wrote error report: {report_path} ({len(rejected_rows)} rejected rows)")

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
    print(f"  rejected_before_import: {result.rejected_before_import}")
    print(f"  media_items_created: {result.media_items_created}")
    print(f"  shows_created: {result.shows_created}")
    print(f"  cursor_before: {result.cursor_before}")
    print(f"  cursor_after: {result.cursor_after}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
