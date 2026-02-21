import csv
import io
import json
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.auth import require_request_auth
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.scripts import import_watch_events as import_watch_events_script
from app.schemas.imports import (
    ImportMode,
    LegacySourceWatchEventImportRequest,
    WatchEventImportRequest,
    WatchEventImportResponse,
)
from app.services.imports import WatchEventImportResult, WatchEventImportService

router = APIRouter(
    prefix="/imports",
    tags=["imports"],
    dependencies=[Depends(require_request_auth)],
)


def _to_import_response(result: WatchEventImportResult) -> WatchEventImportResponse:
    return WatchEventImportResponse(
        import_batch_id=result.import_batch_id,
        status=result.status,
        dry_run=result.dry_run,
        processed_count=result.processed_count,
        inserted_count=result.inserted_count,
        skipped_count=result.skipped_count,
        error_count=result.error_count,
        rejected_before_import=result.rejected_before_import,
        media_items_created=result.media_items_created,
        shows_created=result.shows_created,
        cursor_before=result.cursor_before,
        cursor_after=result.cursor_after,
    )


def _detect_upload_format(filename: str | None, explicit_format: str) -> str:
    if explicit_format in {"json", "csv"}:
        return explicit_format

    if filename:
        lowered = filename.lower()
        if lowered.endswith(".json"):
            return "json"
        if lowered.endswith(".csv"):
            return "csv"

    raise ValueError(
        "Could not detect upload format from filename. Select file_format=json or file_format=csv."
    )


def _load_json_rows_from_text(file_text: str) -> list[dict]:
    parsed = json.loads(file_text)

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


def _load_csv_rows_from_text(file_text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(file_text))
    rows: list[dict] = []
    for row in reader:
        cleaned = {key: value for key, value in row.items() if key is not None}
        rows.append(cleaned)
    return rows


def _load_uploaded_rows(file_text: str, file_format: str) -> list[dict]:
    if file_format == "json":
        return _load_json_rows_from_text(file_text)
    if file_format == "csv":
        return _load_csv_rows_from_text(file_text)
    raise ValueError(f"Unsupported format: {file_format}")


@router.post("/watch-events", response_model=WatchEventImportResponse)
def import_watch_events(
    payload: WatchEventImportRequest,
    session: Session = Depends(get_db_session),
) -> WatchEventImportResponse:
    try:
        result = WatchEventImportService.run_import(session, payload=payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return _to_import_response(result)


@router.post("/watch-events/legacy-source", response_model=WatchEventImportResponse)
def import_legacy_source_watch_events(
    payload: LegacySourceWatchEventImportRequest,
    session: Session = Depends(get_db_session),
) -> WatchEventImportResponse:
    result = WatchEventImportService.run_legacy_source_import(session, payload=payload)
    return _to_import_response(result)


@router.post(
    "/watch-events/legacy-source/upload", response_model=WatchEventImportResponse
)
async def import_legacy_source_watch_events_upload(
    input_file: UploadFile = File(...),
    input_schema: Literal["mapped_rows", "legacy_backup"] = Form(
        default="legacy_backup"
    ),
    file_format: Literal["auto", "json", "csv"] = Form(default="auto"),
    user_id: UUID | None = Form(default=None),
    mode: ImportMode = Form(default=ImportMode.bootstrap),
    dry_run: bool = Form(default=False),
    resume_from_latest: bool = Form(default=False),
    source_detail: str | None = Form(default=None),
    notes: str | None = Form(default=None),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> WatchEventImportResponse:
    rejected_rows: list[dict] = []
    media_items_created = 0
    shows_created = 0
    try:
        raw_bytes = await input_file.read()
        if not raw_bytes:
            raise ValueError("Uploaded file is empty")
        max_upload_bytes = max(1, settings.klug_import_upload_max_mb) * 1024 * 1024
        if len(raw_bytes) > max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=(
                    f"Uploaded file exceeds max size of "
                    f"{settings.klug_import_upload_max_mb} MB"
                ),
            )

        file_text = raw_bytes.decode("utf-8")
        detected_format = _detect_upload_format(input_file.filename, file_format)
        raw_rows = _load_uploaded_rows(file_text, detected_format)
        rows_for_validation = raw_rows

        if input_schema == "legacy_backup":
            if user_id is None:
                raise ValueError("user_id is required for input_schema=legacy_backup")

            preprocess = (
                import_watch_events_script._build_mapped_rows_from_legacy_backup(
                    raw_rows,
                    user_id=user_id,
                    dry_run=dry_run,
                )
            )
            rows_for_validation = preprocess.mapped_rows
            rejected_rows = preprocess.rejected_rows
            media_items_created = preprocess.media_items_created
            shows_created = preprocess.shows_created

        if not rows_for_validation:
            raise ValueError("No valid rows available for import")

        payload = LegacySourceWatchEventImportRequest(
            mode=mode,
            dry_run=dry_run,
            resume_from_latest=resume_from_latest,
            source_detail=source_detail,
            notes=notes,
            rejected_before_import=len(rejected_rows),
            media_items_created=media_items_created,
            shows_created=shows_created,
            rows=rows_for_validation,
        )
    except HTTPException:
        raise
    except (
        ValueError,
        UnicodeDecodeError,
        ValidationError,
        json.JSONDecodeError,
        csv.Error,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    result = WatchEventImportService.run_legacy_source_import(session, payload=payload)
    return _to_import_response(result)
