from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.horrorfest import HorrorfestService


def _set_permissive_auth(monkeypatch) -> None:
    monkeypatch.setenv("KLUG_API_KEY", "")
    monkeypatch.setenv("KLUG_API_AUTH_MODE", "write")
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("KLUG_SESSION_PASSWORD", "")
    monkeypatch.setenv("KLUG_SESSION_SECRET", "")
    get_settings.cache_clear()


def test_list_horrorfest_years_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "list_years",
        lambda _session: [
            {
                "horrorfest_year": 2026,
                "window_start_at": datetime.now(UTC),
                "window_end_at": datetime.now(UTC),
                "label": "Horrorfest 2026",
                "notes": None,
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": None,
                "entry_count": 2,
                "total_runtime_seconds": 7200,
                "average_rating_value": None,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/years")

    assert response.status_code == 200
    assert response.json()[0]["horrorfest_year"] == 2026


def test_list_horrorfest_entries_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    entry_id = uuid4()
    watch_id = uuid4()
    monkeypatch.setattr(
        HorrorfestService,
        "list_entries",
        lambda *_args, **_kwargs: [
            {
                "horrorfest_entry_id": entry_id,
                "watch_id": watch_id,
                "horrorfest_year": 2026,
                "watch_order": 1,
                "source_kind": "auto_live",
                "created_at": datetime.now(UTC),
                "updated_at": None,
                "updated_by": None,
                "update_reason": None,
                "is_removed": False,
                "removed_at": None,
                "removed_by": None,
                "removed_reason": None,
                "user_id": uuid4(),
                "media_item_id": uuid4(),
                "watched_at": datetime.now(UTC),
                "playback_source": "kodi",
                "media_item_title": "The Thing",
                "media_item_type": "movie",
                "display_title": "The Thing (1982)",
                "rating_value": None,
                "rating_scale": None,
                "effective_runtime_seconds": 6540,
                "rewatch": False,
                "completed": True,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/years/2026/entries")

    assert response.status_code == 200
    assert response.json()[0]["watch_order"] == 1


def test_include_watch_event_in_horrorfest_returns_row(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    watch_id = uuid4()
    entry_id = uuid4()

    class DummyEntry:
        horrorfest_year = 2026

    monkeypatch.setattr(
        HorrorfestService,
        "include_watch_event",
        lambda *_args, **_kwargs: DummyEntry(),
    )
    monkeypatch.setattr(
        HorrorfestService,
        "list_entries",
        lambda *_args, **_kwargs: [
            {
                "horrorfest_entry_id": entry_id,
                "watch_id": watch_id,
                "horrorfest_year": 2026,
                "watch_order": 2,
                "source_kind": "manual",
                "created_at": datetime.now(UTC),
                "updated_at": None,
                "updated_by": "tester",
                "update_reason": None,
                "is_removed": False,
                "removed_at": None,
                "removed_by": None,
                "removed_reason": None,
                "user_id": uuid4(),
                "media_item_id": uuid4(),
                "watched_at": datetime.now(UTC),
                "playback_source": "kodi",
                "media_item_title": "Alien",
                "media_item_type": "movie",
                "display_title": "Alien (1979)",
                "rating_value": None,
                "rating_scale": None,
                "effective_runtime_seconds": 7020,
                "rewatch": False,
                "completed": True,
            }
        ],
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/horrorfest/watch-events/{watch_id}/include",
        json={"horrorfest_year": 2026, "updated_by": "tester", "update_reason": None},
    )

    assert response.status_code == 200
    assert response.json()["horrorfest_year"] == 2026


def test_list_horrorfest_analytics_years_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "list_analytics_years",
        lambda *_args, **_kwargs: [
            {
                "horrorfest_year": 2025,
                "watch_count": 206,
                "watch_days": 43,
                "new_watch_count": 131,
                "rewatch_count": 75,
                "total_runtime_seconds": 1245240,
                "total_runtime_hours": Decimal("345.90"),
                "average_watches_per_day": Decimal("4.79"),
                "average_runtime_hours_per_day": Decimal("8.04"),
                "average_runtime_minutes_per_watch": Decimal("100.70"),
                "average_rating_value": Decimal("7.60"),
                "rated_watch_count": 206,
                "first_watch_at": datetime.now(UTC),
                "latest_watch_at": datetime.now(UTC),
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/years")

    assert response.status_code == 200
    assert response.json()[0]["horrorfest_year"] == 2025
    assert response.json()[0]["watch_count"] == 206


def test_get_horrorfest_analytics_year_detail_returns_payload(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_year_detail",
        lambda *_args, **_kwargs: {
            "summary": {
                "horrorfest_year": 2025,
                "watch_count": 206,
                "watch_days": 43,
                "new_watch_count": 131,
                "rewatch_count": 75,
                "total_runtime_seconds": 1245240,
                "total_runtime_hours": Decimal("345.90"),
                "average_watches_per_day": Decimal("4.79"),
                "average_runtime_hours_per_day": Decimal("8.04"),
                "average_runtime_minutes_per_watch": Decimal("100.70"),
                "average_rating_value": Decimal("7.60"),
                "rated_watch_count": 206,
                "first_watch_at": datetime.now(UTC),
                "latest_watch_at": datetime.now(UTC),
            },
            "daily_rows": [
                {
                    "watch_date": "2025-10-01",
                    "watch_count": 5,
                    "total_runtime_seconds": 28800,
                    "total_runtime_hours": Decimal("8.00"),
                    "average_rating_value": Decimal("7.40"),
                }
            ],
            "source_rows": [
                {
                    "playback_source": "kodi",
                    "watch_count": 150,
                    "total_runtime_seconds": 972000,
                    "total_runtime_hours": Decimal("270.00"),
                    "average_rating_value": Decimal("7.20"),
                }
            ],
            "rating_rows": [
                {
                    "rating_value": Decimal("8.00"),
                    "watch_count": 42,
                }
            ],
        },
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/years/2025")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["horrorfest_year"] == 2025
    assert payload["daily_rows"][0]["watch_count"] == 5
    assert payload["source_rows"][0]["playback_source"] == "kodi"
    assert payload["rating_rows"][0]["watch_count"] == 42


def test_get_horrorfest_analytics_year_detail_returns_not_found(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)

    def _raise_not_found(*_args, **_kwargs):
        raise ValueError("Horrorfest year '1999' not found")

    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_year_detail",
        _raise_not_found,
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/years/1999")

    assert response.status_code == 404


def test_get_horrorfest_analytics_title_matrix_returns_payload(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_title_matrix",
        lambda *_args, **_kwargs: {
            "years": [2025, 2024, 2023],
            "rows": [
                {
                    "media_item_id": uuid4(),
                    "title": "Ghost Mansion",
                    "total_count": 3,
                    "year_counts": {"2025": 1, "2024": 2, "2023": 0},
                }
            ],
        },
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/titles")

    assert response.status_code == 200
    payload = response.json()
    assert payload["years"] == [2025, 2024, 2023]
    assert payload["rows"][0]["title"] == "Ghost Mansion"
    assert payload["rows"][0]["year_counts"]["2024"] == 2


def test_get_horrorfest_analytics_decade_matrix_returns_payload(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_decade_matrix",
        lambda *_args, **_kwargs: {
            "years": [2025, 2024, 2023],
            "rows": [
                {
                    "decade": "1980s",
                    "total_count": 12,
                    "year_counts": {"2025": 5, "2024": 4, "2023": 3},
                }
            ],
        },
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/decades")

    assert response.status_code == 200
    payload = response.json()
    assert payload["rows"][0]["decade"] == "1980s"
    assert payload["rows"][0]["total_count"] == 12
