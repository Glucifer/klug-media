from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.imports import WatchEventImportResult, WatchEventImportService


def test_import_watch_events_returns_summary(monkeypatch) -> None:
    expected_result = WatchEventImportResult(
        import_batch_id=uuid4(),
        status="completed_with_errors",
        dry_run=False,
        processed_count=3,
        inserted_count=1,
        skipped_count=1,
        error_count=1,
    )

    def fake_run_import(_session, *, payload):
        assert payload.mode.value == "bootstrap"
        return expected_result

    monkeypatch.setattr(WatchEventImportService, "run_import", fake_run_import)

    client = TestClient(app)
    response = client.post(
        "/api/v1/imports/watch-events",
        json={
            "source": "legacy_source_export",
            "mode": "bootstrap",
            "events": [
                {
                    "user_id": str(uuid4()),
                    "media_item_id": str(uuid4()),
                    "watched_at": datetime.now(UTC).isoformat(),
                    "playback_source": "jellyfin",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["processed_count"] == 3
    assert payload["inserted_count"] == 1
    assert payload["skipped_count"] == 1
    assert payload["error_count"] == 1


def test_import_watch_events_unsupported_source_returns_422(monkeypatch) -> None:
    def fake_run_import(_session, *, payload):
        raise ValueError("Unsupported import source: unknown")

    monkeypatch.setattr(WatchEventImportService, "run_import", fake_run_import)

    client = TestClient(app)
    response = client.post(
        "/api/v1/imports/watch-events",
        json={
            "source": "unknown",
            "mode": "incremental",
            "events": [
                {
                    "user_id": str(uuid4()),
                    "media_item_id": str(uuid4()),
                    "watched_at": datetime.now(UTC).isoformat(),
                    "playback_source": "jellyfin",
                }
            ],
        },
    )

    assert response.status_code == 422


def test_import_legacy_source_watch_events_endpoint(monkeypatch) -> None:
    expected_result = WatchEventImportResult(
        import_batch_id=uuid4(),
        status="dry_run",
        dry_run=True,
        processed_count=1,
        inserted_count=1,
        skipped_count=0,
        error_count=0,
    )

    def fake_run_legacy_source_import(_session, *, payload):
        assert payload.mode.value == "incremental"
        assert payload.dry_run is True
        return expected_result

    monkeypatch.setattr(
        WatchEventImportService,
        "run_legacy_source_import",
        fake_run_legacy_source_import,
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/imports/watch-events/legacy-source",
        json={
            "mode": "incremental",
            "dry_run": True,
            "rows": [
                {
                    "user_id": str(uuid4()),
                    "media_item_id": str(uuid4()),
                    "watched_at": datetime.now(UTC).isoformat(),
                    "player": "jellyfin",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "dry_run"
