import json
from datetime import UTC, datetime
from uuid import uuid4


def test_upload_import_dry_run_returns_summary_and_cursor(integration_client) -> None:
    watched_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    payload_rows = [
        {
            "user_id": str(uuid4()),
            "media_item_id": str(uuid4()),
            "watched_at": watched_at,
            "player": "legacy_backup",
            "source_event_id": "upload-evt-1",
            "completed": True,
        }
    ]

    response = integration_client.post(
        "/api/v1/imports/watch-events/legacy-source/upload",
        data={
            "input_schema": "mapped_rows",
            "file_format": "json",
            "mode": "incremental",
            "dry_run": "true",
            "resume_from_latest": "false",
        },
        files={
            "input_file": (
                "upload_history.json",
                json.dumps(payload_rows),
                "application/json",
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "dry_run"
    assert data["dry_run"] is True
    assert data["processed_count"] == 1
    assert data["inserted_count"] == 1
    assert data["skipped_count"] == 0
    assert data["error_count"] == 0
    assert data["cursor_before"] is None
    assert data["cursor_after"]["watched_at"] == watched_at
    assert data["cursor_after"]["source_event_id"] == "upload-evt-1"
