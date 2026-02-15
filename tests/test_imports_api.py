from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.imports import WatchEventImportResult, WatchEventImportService


def test_import_watch_events_returns_summary(monkeypatch) -> None:
    expected_result = WatchEventImportResult(
        import_batch_id=uuid4(),
        status="completed_with_errors",
        processed_count=2,
        inserted_count=1,
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
    assert payload["processed_count"] == 2
    assert payload["inserted_count"] == 1
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
