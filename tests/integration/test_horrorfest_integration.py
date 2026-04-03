from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from app.db.models.entities import HorrorfestEntry, HorrorfestYear, MediaItem, User, WatchEvent


def test_horrorfest_title_drilldown_excludes_removed_and_deleted_and_orders_rows(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username=f"horrorfest-title-{uuid4().hex[:8]}")
    movie = MediaItem(type="movie", title="The Thing", year=1982, base_runtime_seconds=6540)
    session.add_all(
        [
            user,
            movie,
            HorrorfestYear(
                horrorfest_year=2025,
                window_start_at=datetime.fromisoformat("2025-10-01T00:00:00+00:00"),
                window_end_at=datetime.fromisoformat("2025-10-31T23:59:59+00:00"),
                label="Horrorfest 2025",
                is_active=True,
            ),
            HorrorfestYear(
                horrorfest_year=2026,
                window_start_at=datetime.fromisoformat("2026-10-01T00:00:00+00:00"),
                window_end_at=datetime.fromisoformat("2026-10-31T23:59:59+00:00"),
                label="Horrorfest 2026",
                is_active=True,
            ),
        ]
    )
    session.flush()

    watch_2026_first = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2026-10-04T03:00:00+00:00"),
        playback_source="integration",
        completed=True,
    )
    watch_2026_second = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2026-10-07T03:00:00+00:00"),
        playback_source="integration",
        completed=True,
        rewatch=True,
    )
    watch_2025_active = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-09T03:00:00+00:00"),
        playback_source="integration",
        completed=True,
        rewatch=True,
    )
    watch_2025_removed = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-12T03:00:00+00:00"),
        playback_source="integration",
        completed=True,
        rewatch=True,
    )
    watch_2025_deleted = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-15T03:00:00+00:00"),
        playback_source="integration",
        completed=True,
        is_deleted=True,
        rewatch=True,
    )
    session.add_all(
        [
            watch_2026_first,
            watch_2026_second,
            watch_2025_active,
            watch_2025_removed,
            watch_2025_deleted,
        ]
    )
    session.flush()
    session.add_all(
        [
            HorrorfestEntry(
                watch_id=watch_2026_second.watch_id,
                horrorfest_year=2026,
                watch_order=2,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=watch_2026_first.watch_id,
                horrorfest_year=2026,
                watch_order=1,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=watch_2025_active.watch_id,
                horrorfest_year=2025,
                watch_order=3,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=watch_2025_removed.watch_id,
                horrorfest_year=2025,
                watch_order=4,
                source_kind="manual",
                is_removed=True,
            ),
            HorrorfestEntry(
                watch_id=watch_2025_deleted.watch_id,
                horrorfest_year=2025,
                watch_order=5,
                source_kind="manual",
            ),
        ]
    )
    session.commit()
    session.close()

    response = integration_client.get(
        f"/api/v1/horrorfest/analytics/titles/{movie.media_item_id}/entries?user_id={user.user_id}"
    )

    assert response.status_code == 200
    payload = response.json()
    assert [(row["horrorfest_year"], row["watch_order"]) for row in payload] == [
        (2026, 1),
        (2026, 2),
        (2025, 3),
    ]
    assert all(row["is_removed"] is False for row in payload)
    assert all(row["watch_id"] != str(watch_2025_deleted.watch_id) for row in payload)


def test_horrorfest_decade_drilldown_honors_year_and_decade_scope(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username=f"horrorfest-decade-{uuid4().hex[:8]}")
    eighties_movie = MediaItem(type="movie", title="The Blob", year=1988, base_runtime_seconds=5700)
    seventies_movie = MediaItem(type="movie", title="Halloween", year=1978, base_runtime_seconds=5460)
    nineties_movie = MediaItem(type="movie", title="Candyman", year=1992, base_runtime_seconds=5940)
    session.add_all(
        [
            user,
            eighties_movie,
            seventies_movie,
            nineties_movie,
            HorrorfestYear(
                horrorfest_year=2025,
                window_start_at=datetime.fromisoformat("2025-10-01T00:00:00+00:00"),
                window_end_at=datetime.fromisoformat("2025-10-31T23:59:59+00:00"),
                label="Horrorfest 2025",
                is_active=True,
            ),
            HorrorfestYear(
                horrorfest_year=2026,
                window_start_at=datetime.fromisoformat("2026-10-01T00:00:00+00:00"),
                window_end_at=datetime.fromisoformat("2026-10-31T23:59:59+00:00"),
                label="Horrorfest 2026",
                is_active=True,
            ),
        ]
    )
    session.flush()

    active_eighties_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=eighties_movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-05T04:00:00+00:00"),
        playback_source="integration",
        completed=True,
    )
    later_year_eighties_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=eighties_movie.media_item_id,
        watched_at=datetime.fromisoformat("2026-10-05T04:00:00+00:00"),
        playback_source="integration",
        completed=True,
        rewatch=True,
    )
    seventies_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=seventies_movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-07T04:00:00+00:00"),
        playback_source="integration",
        completed=True,
    )
    nineties_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=nineties_movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-08T04:00:00+00:00"),
        playback_source="integration",
        completed=True,
    )
    removed_eighties_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=eighties_movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-09T04:00:00+00:00"),
        playback_source="integration",
        completed=True,
        rewatch=True,
    )
    session.add_all(
        [
            active_eighties_watch,
            later_year_eighties_watch,
            seventies_watch,
            nineties_watch,
            removed_eighties_watch,
        ]
    )
    session.flush()
    session.add_all(
        [
            HorrorfestEntry(
                watch_id=active_eighties_watch.watch_id,
                horrorfest_year=2025,
                watch_order=1,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=later_year_eighties_watch.watch_id,
                horrorfest_year=2026,
                watch_order=1,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=seventies_watch.watch_id,
                horrorfest_year=2025,
                watch_order=2,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=nineties_watch.watch_id,
                horrorfest_year=2025,
                watch_order=3,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=removed_eighties_watch.watch_id,
                horrorfest_year=2025,
                watch_order=4,
                source_kind="manual",
                is_removed=True,
            ),
        ]
    )
    session.commit()
    session.close()

    response = integration_client.get(
        f"/api/v1/horrorfest/analytics/decades/1980/entries?horrorfest_year=2025&user_id={user.user_id}"
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["display_title"] == "The Blob (1988)"
    assert payload[0]["horrorfest_year"] == 2025
    assert payload[0]["watch_id"] != str(removed_eighties_watch.watch_id)
