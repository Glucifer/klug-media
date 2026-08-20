from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.jellyfin_integration import (
    JellyfinIntegrationService,
    JellyfinIntegrationStatus,
    JellyfinUserMapping,
)
from app.services.users import JellyfinUserAlreadyMappedError, UserService


JELLYFIN_USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_list_jellyfin_users_returns_mapping(monkeypatch) -> None:
    klug_user_id = uuid4()
    monkeypatch.setattr(
        JellyfinIntegrationService,
        "list_user_mappings",
        lambda *_args, **_kwargs: [
            JellyfinUserMapping(
                jellyfin_user_id=JELLYFIN_USER_ID,
                jellyfin_username="Travis",
                klug_user_id=klug_user_id,
                klug_username="travis",
            )
        ],
    )

    response = TestClient(app).get("/api/v1/integrations/jellyfin/users")

    assert response.status_code == 200
    assert response.json()[0]["jellyfin_username"] == "Travis"
    assert response.json()[0]["klug_user_id"] == str(klug_user_id)


def test_status_does_not_expose_credentials(monkeypatch) -> None:
    monkeypatch.setattr(
        JellyfinIntegrationService,
        "get_status",
        lambda *_args, **_kwargs: JellyfinIntegrationStatus(
            configured=True,
            connected=True,
            connection_error=None,
            mapped_user_count=1,
            latest_webhook_at=datetime(2026, 8, 20, tzinfo=UTC),
            latest_webhook_decision="watch_event_created",
            latest_reconciliation_at=None,
            latest_reconciliation_status=None,
        ),
    )

    response = TestClient(app).get("/api/v1/integrations/jellyfin/status")

    assert response.status_code == 200
    assert response.json()["connected"] is True
    assert "api_key" not in response.text.lower()


def test_update_mapping_returns_409_for_duplicate(monkeypatch) -> None:
    def duplicate(*_args, **_kwargs):
        raise JellyfinUserAlreadyMappedError(str(JELLYFIN_USER_ID))

    monkeypatch.setattr(UserService, "update_jellyfin_user_mapping", duplicate)

    response = TestClient(app).put(
        f"/api/v1/integrations/jellyfin/users/{uuid4()}",
        json={"jellyfin_user_id": str(JELLYFIN_USER_ID)},
    )

    assert response.status_code == 409


def test_update_mapping_can_clear_mapping(monkeypatch) -> None:
    monkeypatch.setattr(
        UserService,
        "update_jellyfin_user_mapping",
        lambda *_args, **_kwargs: SimpleNamespace(jellyfin_user_id=None),
    )

    response = TestClient(app).put(
        f"/api/v1/integrations/jellyfin/users/{uuid4()}",
        json={"jellyfin_user_id": None},
    )

    assert response.status_code == 200
    assert response.json() == {"jellyfin_user_id": None}
