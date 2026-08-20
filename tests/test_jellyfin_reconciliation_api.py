from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.jellyfin_integration import JellyfinReconcileRead
from app.services.jellyfin import JellyfinClientError
from app.services.jellyfin_reconciliation import JellyfinReconciliationService


def _request_payload() -> dict:
    return {
        "klug_user_id": str(uuid4()),
        "dry_run": True,
    }


def test_reconcile_endpoint_returns_summary(monkeypatch) -> None:
    now = datetime(2026, 8, 20, 12, tzinfo=UTC)
    monkeypatch.setattr(
        JellyfinReconciliationService,
        "run",
        lambda *_args, **_kwargs: JellyfinReconcileRead(
            import_batch_id=UUID(int=0),
            status="dry_run",
            dry_run=True,
            since=now,
            cursor_after=now,
            scanned_count=4,
            candidate_count=2,
            inserted_count=1,
            already_present_count=1,
            unmatched_media_count=0,
            missing_timestamp_count=0,
            ambiguous_play_count=0,
            error_count=0,
            issue_count=0,
            issues=[],
        ),
    )

    response = TestClient(app).post(
        "/api/v1/imports/watch-events/jellyfin/reconcile",
        json=_request_payload(),
    )

    assert response.status_code == 200
    assert response.json()["inserted_count"] == 1
    assert response.json()["dry_run"] is True


def test_reconcile_endpoint_maps_jellyfin_failure_to_502(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise JellyfinClientError("Jellyfin request failed")

    monkeypatch.setattr(JellyfinReconciliationService, "run", fail)

    response = TestClient(app).post(
        "/api/v1/imports/watch-events/jellyfin/reconcile",
        json=_request_payload(),
    )

    assert response.status_code == 502
