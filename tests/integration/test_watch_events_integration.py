from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from app.db.models.entities import MediaItem, User


def test_post_watch_event_success(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username="integration-user")
    media_item = MediaItem(type="movie", title="Integration Movie")
    session.add_all([user, media_item])
    session.commit()
    session.refresh(user)
    session.refresh(media_item)
    session.close()

    response = integration_client.post(
        "/api/v1/watch-events",
        json={
            "user_id": str(user.user_id),
            "media_item_id": str(media_item.media_item_id),
            "watched_at": datetime.now(UTC).isoformat(),
            "playback_source": "jellyfin",
            "completed": True,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["user_id"] == str(user.user_id)
    assert payload["media_item_id"] == str(media_item.media_item_id)
    assert payload["playback_source"] == "jellyfin"


def test_post_watch_event_fk_violation_returns_409(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    media_item = MediaItem(type="movie", title="Integration Movie")
    session.add(media_item)
    session.commit()
    session.refresh(media_item)
    session.close()

    response = integration_client.post(
        "/api/v1/watch-events",
        json={
            "user_id": str(uuid4()),
            "media_item_id": str(media_item.media_item_id),
            "watched_at": datetime.now(UTC).isoformat(),
            "playback_source": "jellyfin",
            "completed": True,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Watch event failed database constraints"
