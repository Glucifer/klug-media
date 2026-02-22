from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from app.db.models.entities import MediaItem, User, WatchEvent


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
    assert payload["watched_at"].endswith("Z")
    assert payload["created_at"].endswith("Z")


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


def test_list_watch_events_applies_user_local_date_filters(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username="local-date-user", timezone="America/Edmonton")
    media_item = MediaItem(type="movie", title="Local Date Movie")
    session.add_all([user, media_item])
    session.flush()
    session.add_all(
        [
            WatchEvent(
                user_id=user.user_id,
                media_item_id=media_item.media_item_id,
                watched_at=datetime.fromisoformat("2026-01-02T00:30:00+00:00"),
                playback_source="integration",
                completed=True,
            ),
            WatchEvent(
                user_id=user.user_id,
                media_item_id=media_item.media_item_id,
                watched_at=datetime.fromisoformat("2026-01-02T09:00:00+00:00"),
                playback_source="integration",
                completed=True,
            ),
        ]
    )
    session.commit()
    session.close()

    response_local_day = integration_client.get(
        f"/api/v1/watch-events?user_id={user.user_id}&local_date_from=2026-01-01&local_date_to=2026-01-01"
    )
    assert response_local_day.status_code == 200
    payload_local_day = response_local_day.json()
    assert len(payload_local_day) == 1
    assert payload_local_day[0]["watched_at"] == "2026-01-02T00:30:00Z"
    assert payload_local_day[0]["watched_at_local"] == "2026-01-01T17:30:00-07:00"
    assert payload_local_day[0]["user_timezone"] == "America/Edmonton"

    response_utc_day_only = integration_client.get(
        f"/api/v1/watch-events?user_id={user.user_id}&local_date_from=2026-01-02&local_date_to=2026-01-02"
    )
    assert response_utc_day_only.status_code == 200
    payload_utc_day_only = response_utc_day_only.json()
    assert len(payload_utc_day_only) == 1
    assert payload_utc_day_only[0]["watched_at"] == "2026-01-02T09:00:00Z"
