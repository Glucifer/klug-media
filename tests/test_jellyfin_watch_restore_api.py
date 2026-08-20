from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.jellyfin_integration import JellyfinWatchRestoreRead
from app.services.jellyfin import JellyfinClientError
from app.services.jellyfin_watch_restore import JellyfinWatchRestoreService


USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_restore_endpoint_returns_summary(monkeypatch) -> None:
    monkeypatch.setattr(
        JellyfinWatchRestoreService,
        "run",
        lambda *_args, **_kwargs: JellyfinWatchRestoreRead(
            import_batch_id=UUID(int=0),
            status="dry_run",
            dry_run=True,
            eligible_count=100,
            already_played_count=20,
            candidate_count=80,
            attempted_count=0,
            restored_count=0,
            remaining_count=80,
            movie_candidate_count=30,
            episode_candidate_count=50,
            error_count=0,
            issues=[],
        ),
    )

    response = TestClient(app).post(
        "/api/v1/integrations/jellyfin/watch-state/restore",
        json={"klug_user_id": str(USER_ID), "dry_run": True},
    )

    assert response.status_code == 200
    assert response.json()["candidate_count"] == 80


def test_restore_endpoint_maps_jellyfin_failure_to_502(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise JellyfinClientError("Jellyfin request failed")

    monkeypatch.setattr(JellyfinWatchRestoreService, "run", fail)

    response = TestClient(app).post(
        "/api/v1/integrations/jellyfin/watch-state/restore",
        json={"klug_user_id": str(USER_ID), "dry_run": True},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Jellyfin request failed"
