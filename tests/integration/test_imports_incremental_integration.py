from datetime import UTC, datetime

from sqlalchemy.orm import Session, sessionmaker

from app.db.models.entities import MediaItem, User


def test_incremental_reimport_skips_existing_source_event_id(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username="incremental-user")
    media_item = MediaItem(type="movie", title="Incremental Movie")
    session.add_all([user, media_item])
    session.commit()
    session.refresh(user)
    session.refresh(media_item)
    session.close()

    payload = {
        "mode": "incremental",
        "resume_from_latest": False,
        "rows": [
            {
                "user_id": str(user.user_id),
                "media_item_id": str(media_item.media_item_id),
                "watched_at": datetime.now(UTC).isoformat(),
                "player": "jellyfin",
                "source_event_id": "legacy-evt-001",
                "completed": True,
            }
        ],
    }

    first_response = integration_client.post(
        "/api/v1/imports/watch-events/legacy-source",
        json=payload,
    )
    assert first_response.status_code == 200
    first_data = first_response.json()
    assert first_data["inserted_count"] == 1
    assert first_data["skipped_count"] == 0
    assert first_data["error_count"] == 0

    second_response = integration_client.post(
        "/api/v1/imports/watch-events/legacy-source",
        json=payload,
    )
    assert second_response.status_code == 200
    second_data = second_response.json()
    assert second_data["inserted_count"] == 0
    assert second_data["skipped_count"] == 1
    assert second_data["error_count"] == 0
