from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from app.db.models.entities import (
    HorrorfestEntry,
    HorrorfestYear,
    MediaItem,
    MediaVersion,
    User,
    WatchEvent,
)


def test_stats_summary_uses_effective_runtime_and_excludes_deleted(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username=f"stats-user-{uuid4().hex[:8]}", timezone="America/Edmonton")
    movie = MediaItem(type="movie", title="Stats Movie", base_runtime_seconds=6000)
    episode = MediaItem(type="episode", title="Stats Episode", season_number=1, episode_number=1)
    session.add_all([user, movie, episode])
    session.flush()
    media_version = MediaVersion(
        media_item_id=movie.media_item_id,
        version_key="directors_cut",
        version_name="Director's Cut",
        runtime_seconds=6600,
    )
    session.add(media_version)
    session.flush()
    session.add_all(
        [
            WatchEvent(
                user_id=user.user_id,
                media_item_id=movie.media_item_id,
                media_version_id=media_version.media_version_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
                rating_value=Decimal("8"),
                rating_scale="10-star",
            ),
            WatchEvent(
                user_id=user.user_id,
                media_item_id=episode.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
                watch_runtime_seconds=1800,
                rewatch=True,
            ),
            WatchEvent(
                user_id=user.user_id,
                media_item_id=movie.media_item_id,
                watched_at=datetime.now(UTC),
                playback_source="integration",
                completed=True,
                is_deleted=True,
                watch_runtime_seconds=9999,
            ),
        ]
    )
    session.commit()
    session.close()

    response = integration_client.get(f"/api/v1/stats/summary?user_id={user.user_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_active_watches"] == 2
    assert payload["total_completed_watches"] == 2
    assert payload["movie_watch_count"] == 1
    assert payload["episode_watch_count"] == 1
    assert payload["total_rewatches"] == 1
    assert payload["unrated_completed_watch_count"] == 1
    assert payload["total_watch_time_seconds"] == 8400
    assert payload["total_watch_time_hours"] == "2.33"
    assert payload["average_rating_value"] == "8"


def test_stats_monthly_uses_user_local_month_boundary(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username=f"monthly-user-{uuid4().hex[:8]}", timezone="America/Edmonton")
    movie = MediaItem(type="movie", title="Boundary Movie", base_runtime_seconds=5400)
    session.add_all([user, movie])
    session.flush()
    session.add_all(
        [
            WatchEvent(
                user_id=user.user_id,
                media_item_id=movie.media_item_id,
                watched_at=datetime.fromisoformat("2026-04-01T00:30:00+00:00"),
                playback_source="integration",
                completed=True,
            ),
            WatchEvent(
                user_id=user.user_id,
                media_item_id=movie.media_item_id,
                watched_at=datetime.fromisoformat("2026-04-01T08:30:00+00:00"),
                playback_source="integration",
                completed=True,
                rating_value=Decimal("9"),
                rating_scale="10-star",
            ),
        ]
    )
    session.commit()
    session.close()

    response = integration_client.get(f"/api/v1/stats/monthly?user_id={user.user_id}")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    months = {(row["year"], row["month"]): row for row in payload}
    assert months[(2026, 4)]["watch_count"] == 1
    assert months[(2026, 4)]["rated_watch_count"] == 1
    assert months[(2026, 3)]["watch_count"] == 1


def test_stats_horrorfest_excludes_removed_and_deleted_watches(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username=f"horror-user-{uuid4().hex[:8]}")
    year = HorrorfestYear(
        horrorfest_year=2026,
        window_start_at=datetime.fromisoformat("2026-10-01T00:00:00+00:00"),
        window_end_at=datetime.fromisoformat("2026-10-31T23:59:59+00:00"),
        label="Horrorfest 2026",
        is_active=True,
    )
    movie = MediaItem(type="movie", title="Fest Movie", base_runtime_seconds=7200)
    removed_movie = MediaItem(type="movie", title="Removed Fest Movie", base_runtime_seconds=5400)
    deleted_movie = MediaItem(type="movie", title="Deleted Fest Movie", base_runtime_seconds=4800)
    session.add_all([user, year, movie, removed_movie, deleted_movie])
    session.flush()
    active_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.now(UTC),
        playback_source="integration",
        completed=True,
        rating_value=Decimal("7"),
        rating_scale="10-star",
        rewatch=True,
    )
    removed_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=removed_movie.media_item_id,
        watched_at=datetime.now(UTC),
        playback_source="integration",
        completed=True,
    )
    deleted_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=deleted_movie.media_item_id,
        watched_at=datetime.now(UTC),
        playback_source="integration",
        completed=True,
        is_deleted=True,
    )
    session.add_all([active_watch, removed_watch, deleted_watch])
    session.flush()
    session.add_all(
        [
            HorrorfestEntry(
                watch_id=active_watch.watch_id,
                horrorfest_year=2026,
                watch_order=1,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=removed_watch.watch_id,
                horrorfest_year=2026,
                watch_order=None,
                source_kind="manual",
                is_removed=True,
            ),
            HorrorfestEntry(
                watch_id=deleted_watch.watch_id,
                horrorfest_year=2026,
                watch_order=2,
                source_kind="manual",
            ),
        ]
    )
    session.commit()
    session.close()

    response = integration_client.get(f"/api/v1/stats/horrorfest?user_id={user.user_id}")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    row = payload[0]
    assert row["horrorfest_year"] == 2026
    assert row["entry_count"] == 1
    assert row["rated_entry_count"] == 1
    assert row["rewatch_count"] == 1
    assert row["total_runtime_seconds"] == 7200
    assert row["total_runtime_hours"] == "2.00"
