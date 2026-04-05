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


def test_horrorfest_selected_year_drilldown_filters_by_date_source_and_rating(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username=f"horrorfest-year-{uuid4().hex[:8]}", timezone="America/Edmonton")
    movie = MediaItem(type="movie", title="Creepshow", year=1982, base_runtime_seconds=7200)
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
        ]
    )
    session.flush()

    same_local_day_kodi = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-02T05:30:00+00:00"),
        playback_source="kodi",
        completed=True,
        rating_value=8,
        rating_scale="10-star",
    )
    same_local_day_disc = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-02T20:30:00+00:00"),
        playback_source="disc",
        completed=True,
        rating_value=7,
        rating_scale="10-star",
        rewatch=True,
    )
    other_local_day = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-03T06:30:00+00:00"),
        playback_source="kodi",
        completed=True,
        rating_value=8,
        rating_scale="10-star",
        rewatch=True,
    )
    removed_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-02T08:00:00+00:00"),
        playback_source="kodi",
        completed=True,
        rating_value=8,
        rating_scale="10-star",
    )
    deleted_watch = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-02T09:00:00+00:00"),
        playback_source="kodi",
        completed=True,
        rating_value=8,
        rating_scale="10-star",
        is_deleted=True,
    )
    session.add_all(
        [
            same_local_day_kodi,
            same_local_day_disc,
            other_local_day,
            removed_watch,
            deleted_watch,
        ]
    )
    session.flush()
    session.add_all(
        [
            HorrorfestEntry(
                watch_id=same_local_day_kodi.watch_id,
                horrorfest_year=2025,
                watch_order=1,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=same_local_day_disc.watch_id,
                horrorfest_year=2025,
                watch_order=2,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=other_local_day.watch_id,
                horrorfest_year=2025,
                watch_order=3,
                source_kind="manual",
            ),
            HorrorfestEntry(
                watch_id=removed_watch.watch_id,
                horrorfest_year=2025,
                watch_order=4,
                source_kind="manual",
                is_removed=True,
            ),
            HorrorfestEntry(
                watch_id=deleted_watch.watch_id,
                horrorfest_year=2025,
                watch_order=5,
                source_kind="manual",
            ),
        ]
    )
    session.commit()
    session.close()

    date_response = integration_client.get(
        f"/api/v1/horrorfest/analytics/years/2025/entries?watch_date=2025-10-01&user_id={user.user_id}"
    )
    assert date_response.status_code == 200
    date_payload = date_response.json()
    assert [row["watch_order"] for row in date_payload] == [1, 2]

    source_response = integration_client.get(
        f"/api/v1/horrorfest/analytics/years/2025/entries?playback_source=kodi&user_id={user.user_id}"
    )
    assert source_response.status_code == 200
    source_payload = source_response.json()
    assert [row["watch_order"] for row in source_payload] == [1, 3]

    rating_response = integration_client.get(
        f"/api/v1/horrorfest/analytics/years/2025/entries?rating_value=8&user_id={user.user_id}"
    )
    assert rating_response.status_code == 200
    rating_payload = rating_response.json()
    assert [row["watch_order"] for row in rating_payload] == [1, 3]


def test_horrorfest_comparison_returns_deltas_and_repeated_titles(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username=f"horrorfest-compare-{uuid4().hex[:8]}")
    movie = MediaItem(type="movie", title="The Thing", year=1982, base_runtime_seconds=6540)
    session.add_all(
        [
            user,
            movie,
            HorrorfestYear(
                horrorfest_year=2024,
                window_start_at=datetime.fromisoformat("2024-10-01T00:00:00+00:00"),
                window_end_at=datetime.fromisoformat("2024-10-31T23:59:59+00:00"),
                label="Horrorfest 2024",
                is_active=True,
            ),
            HorrorfestYear(
                horrorfest_year=2025,
                window_start_at=datetime.fromisoformat("2025-10-01T00:00:00+00:00"),
                window_end_at=datetime.fromisoformat("2025-10-31T23:59:59+00:00"),
                label="Horrorfest 2025",
                is_active=True,
            ),
        ]
    )
    session.flush()

    watch_2024 = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2024-10-10T04:00:00+00:00"),
        playback_source="disc",
        completed=True,
        rating_value=7,
        rating_scale="10-star",
    )
    watch_2025_first = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-10T04:00:00+00:00"),
        playback_source="kodi",
        completed=True,
        rating_value=8,
        rating_scale="10-star",
    )
    watch_2025_second = WatchEvent(
        user_id=user.user_id,
        media_item_id=movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-12T04:00:00+00:00"),
        playback_source="kodi",
        completed=True,
        rating_value=9,
        rating_scale="10-star",
        rewatch=True,
    )
    session.add_all([watch_2024, watch_2025_first, watch_2025_second])
    session.flush()
    session.add_all(
        [
            HorrorfestEntry(watch_id=watch_2024.watch_id, horrorfest_year=2024, watch_order=1, source_kind="manual"),
            HorrorfestEntry(watch_id=watch_2025_first.watch_id, horrorfest_year=2025, watch_order=1, source_kind="manual"),
            HorrorfestEntry(watch_id=watch_2025_second.watch_id, horrorfest_year=2025, watch_order=2, source_kind="manual"),
        ]
    )
    session.commit()
    session.close()

    response = integration_client.get(
        f"/api/v1/horrorfest/analytics/compare?left_year=2025&right_year=2024&user_id={user.user_id}"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["delta"]["watch_count"] == 1
    assert payload["source_rows"][0]["playback_source"] == "kodi"
    assert payload["repeated_title_rows"][0]["title"] == "The Thing (1982)"


def test_horrorfest_repeated_titles_leaderboard_and_export_return_sorted_rows(
    integration_client,
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    user = User(username=f"horrorfest-repeats-{uuid4().hex[:8]}")
    repeated_movie = MediaItem(type="movie", title="Halloween", year=1978, base_runtime_seconds=5460)
    single_movie = MediaItem(type="movie", title="Candyman", year=1992, base_runtime_seconds=5940)
    session.add_all(
        [
            user,
            repeated_movie,
            single_movie,
            HorrorfestYear(
                horrorfest_year=2024,
                window_start_at=datetime.fromisoformat("2024-10-01T00:00:00+00:00"),
                window_end_at=datetime.fromisoformat("2024-10-31T23:59:59+00:00"),
                label="Horrorfest 2024",
                is_active=True,
            ),
            HorrorfestYear(
                horrorfest_year=2025,
                window_start_at=datetime.fromisoformat("2025-10-01T00:00:00+00:00"),
                window_end_at=datetime.fromisoformat("2025-10-31T23:59:59+00:00"),
                label="Horrorfest 2025",
                is_active=True,
            ),
        ]
    )
    session.flush()
    repeated_2024 = WatchEvent(
        user_id=user.user_id,
        media_item_id=repeated_movie.media_item_id,
        watched_at=datetime.fromisoformat("2024-10-10T04:00:00+00:00"),
        playback_source="disc",
        completed=True,
    )
    repeated_2025 = WatchEvent(
        user_id=user.user_id,
        media_item_id=repeated_movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-10T04:00:00+00:00"),
        playback_source="disc",
        completed=True,
        rewatch=True,
    )
    single_2025 = WatchEvent(
        user_id=user.user_id,
        media_item_id=single_movie.media_item_id,
        watched_at=datetime.fromisoformat("2025-10-11T04:00:00+00:00"),
        playback_source="disc",
        completed=True,
    )
    session.add_all([repeated_2024, repeated_2025, single_2025])
    session.flush()
    session.add_all(
        [
            HorrorfestEntry(watch_id=repeated_2024.watch_id, horrorfest_year=2024, watch_order=1, source_kind="manual"),
            HorrorfestEntry(watch_id=repeated_2025.watch_id, horrorfest_year=2025, watch_order=1, source_kind="manual"),
            HorrorfestEntry(watch_id=single_2025.watch_id, horrorfest_year=2025, watch_order=2, source_kind="manual"),
        ]
    )
    session.commit()
    session.close()

    leaderboard_response = integration_client.get(
        f"/api/v1/horrorfest/analytics/leaderboards/repeated-titles?user_id={user.user_id}"
    )
    assert leaderboard_response.status_code == 200
    leaderboard_payload = leaderboard_response.json()
    assert leaderboard_payload["rows"][0]["title"] == "Halloween (1978)"
    assert leaderboard_payload["rows"][0]["total_count"] == 2

    export_response = integration_client.get(
        f"/api/v1/horrorfest/analytics/export/leaderboards/repeated-titles?user_id={user.user_id}"
    )
    assert export_response.status_code == 200
    assert export_response.headers["content-type"].startswith("text/csv")
    assert "Halloween (1978),2" in export_response.text
