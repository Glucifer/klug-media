from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from app.db.models.entities import MediaItem, Show, User, WatchEvent


def _make_tmdb_id() -> int:
    return (uuid4().int % 1_000_000_000) + 1


def test_show_progress_filters_by_user_id(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user_a = User(username=f"user-a-{uuid4().hex[:8]}")
    user_b = User(username=f"user-b-{uuid4().hex[:8]}")
    show = Show(tmdb_id=_make_tmdb_id(), title="Progress Show", year=2024)
    ep1 = MediaItem(
        type="episode",
        title="Episode 1",
        show_id=show.show_id,
        show_tmdb_id=show.tmdb_id,
        season_number=1,
        episode_number=1,
    )
    ep2 = MediaItem(
        type="episode",
        title="Episode 2",
        show_id=show.show_id,
        show_tmdb_id=show.tmdb_id,
        season_number=1,
        episode_number=2,
    )
    session.add_all([user_a, user_b, show, ep1, ep2])
    session.flush()
    session.add_all(
        [
            WatchEvent(
                user_id=user_a.user_id,
                media_item_id=ep1.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
            ),
            WatchEvent(
                user_id=user_a.user_id,
                media_item_id=ep2.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=False,
            ),
            WatchEvent(
                user_id=user_b.user_id,
                media_item_id=ep1.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
            ),
        ]
    )
    session.commit()
    session.close()

    response = integration_client.get(
        f"/api/v1/shows/progress?user_id={user_a.user_id}"
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["show_title"] == "Progress Show"
    assert payload[0]["user_id"] == str(user_a.user_id)
    assert payload[0]["total_episodes"] == 2
    assert payload[0]["watched_episodes"] == 1
    assert payload[0]["watched_percent"] == "50.00"


def test_show_progress_without_user_id_returns_rows_for_watched_users_only(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user_a = User(username=f"user-a-{uuid4().hex[:8]}")
    user_b = User(username=f"user-b-{uuid4().hex[:8]}")
    user_c = User(username=f"user-c-{uuid4().hex[:8]}")
    show = Show(tmdb_id=_make_tmdb_id(), title="All Users Show", year=2024)
    ep1 = MediaItem(
        type="episode",
        title="Episode 1",
        show_id=show.show_id,
        show_tmdb_id=show.tmdb_id,
        season_number=1,
        episode_number=1,
    )
    ep2 = MediaItem(
        type="episode",
        title="Episode 2",
        show_id=show.show_id,
        show_tmdb_id=show.tmdb_id,
        season_number=1,
        episode_number=2,
    )
    session.add_all([user_a, user_b, user_c, show, ep1, ep2])
    session.flush()
    session.add_all(
        [
            WatchEvent(
                user_id=user_a.user_id,
                media_item_id=ep1.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
            ),
            WatchEvent(
                user_id=user_b.user_id,
                media_item_id=ep1.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
            ),
            WatchEvent(
                user_id=user_b.user_id,
                media_item_id=ep2.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
            ),
            # duplicate completed watch on same episode should not increase distinct count
            WatchEvent(
                user_id=user_b.user_id,
                media_item_id=ep2.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
            ),
        ]
    )
    session.commit()
    session.close()

    response = integration_client.get("/api/v1/shows/progress")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2

    rows_by_user_id = {row["user_id"]: row for row in payload}
    row_a = rows_by_user_id[str(user_a.user_id)]
    row_b = rows_by_user_id[str(user_b.user_id)]

    assert row_a["show_title"] == "All Users Show"
    assert row_a["total_episodes"] == 2
    assert row_a["watched_episodes"] == 1
    assert row_a["watched_percent"] == "50.00"

    assert row_b["show_title"] == "All Users Show"
    assert row_b["total_episodes"] == 2
    assert row_b["watched_episodes"] == 2
    assert row_b["watched_percent"] == "100.00"

    # user_c has no completed watches and should not appear in current view definition.
    assert str(user_c.user_id) not in rows_by_user_id
