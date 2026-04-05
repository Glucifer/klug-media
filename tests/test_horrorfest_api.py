from datetime import UTC, date, datetime
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


def test_list_horrorfest_analytics_year_entries_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "list_analytics_year_entries",
        lambda *_args, **_kwargs: [
            {
                "horrorfest_entry_id": uuid4(),
                "watch_id": uuid4(),
                "horrorfest_year": 2025,
                "watch_order": 2,
                "source_kind": "manual",
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
                "rating_value": Decimal("8"),
                "rating_scale": "10-star",
                "effective_runtime_seconds": 6540,
                "rewatch": False,
                "completed": True,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/years/2025/entries")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["horrorfest_year"] == 2025
    assert payload[0]["watch_order"] == 2


def test_list_horrorfest_analytics_year_entries_passes_filters(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    captured = {}

    def fake_list(*_args, **kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(
        HorrorfestService,
        "list_analytics_year_entries",
        fake_list,
    )

    client = TestClient(app)
    response = client.get(
        "/api/v1/horrorfest/analytics/years/2025/entries"
        "?watch_date=2025-10-01&playback_source=kodi&rating_value=8"
    )

    assert response.status_code == 200
    assert captured["horrorfest_year"] == 2025
    assert captured["watch_date"] == date(2025, 10, 1)
    assert captured["playback_source"] == "kodi"
    assert captured["rating_value"] == 8


def test_list_horrorfest_analytics_year_entries_returns_not_found(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)

    def _raise_not_found(*_args, **_kwargs):
        raise ValueError("Horrorfest year '1999' not found")

    monkeypatch.setattr(
        HorrorfestService,
        "list_analytics_year_entries",
        _raise_not_found,
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/years/1999/entries")

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


def test_list_horrorfest_analytics_title_entries_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    media_item_id = uuid4()
    monkeypatch.setattr(
        HorrorfestService,
        "list_analytics_title_entries",
        lambda *_args, **_kwargs: [
            {
                "horrorfest_entry_id": uuid4(),
                "watch_id": uuid4(),
                "horrorfest_year": 2025,
                "watch_order": 4,
                "source_kind": "manual",
                "created_at": datetime.now(UTC),
                "updated_at": None,
                "updated_by": None,
                "update_reason": None,
                "is_removed": False,
                "removed_at": None,
                "removed_by": None,
                "removed_reason": None,
                "user_id": uuid4(),
                "media_item_id": media_item_id,
                "watched_at": datetime.now(UTC),
                "playback_source": "kodi",
                "media_item_title": "The Thing",
                "media_item_type": "movie",
                "display_title": "The Thing (1982)",
                "rating_value": Decimal("9"),
                "rating_scale": "10-star",
                "effective_runtime_seconds": 6540,
                "rewatch": True,
                "completed": True,
            }
        ],
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/horrorfest/analytics/titles/{media_item_id}/entries")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["media_item_id"] == str(media_item_id)
    assert payload[0]["watch_order"] == 4


def test_list_horrorfest_analytics_decade_entries_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "list_analytics_decade_entries",
        lambda *_args, **_kwargs: [
            {
                "horrorfest_entry_id": uuid4(),
                "watch_id": uuid4(),
                "horrorfest_year": 2024,
                "watch_order": 7,
                "source_kind": "manual",
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
                "playback_source": "disc",
                "media_item_title": "Halloween",
                "media_item_type": "movie",
                "display_title": "Halloween (1978)",
                "rating_value": None,
                "rating_scale": None,
                "effective_runtime_seconds": 5460,
                "rewatch": False,
                "completed": True,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/decades/1970/entries?horrorfest_year=2024")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["horrorfest_year"] == 2024
    assert payload[0]["display_title"] == "Halloween (1978)"


def test_list_horrorfest_analytics_decade_entries_returns_422_for_invalid_decade(
    monkeypatch,
) -> None:
    _set_permissive_auth(monkeypatch)

    def _raise_invalid(*_args, **_kwargs):
        raise ValueError("decade_start must be a decade boundary")

    monkeypatch.setattr(
        HorrorfestService,
        "list_analytics_decade_entries",
        _raise_invalid,
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/decades/1977/entries")

    assert response.status_code == 422
    assert response.json()["detail"] == "decade_start must be a decade boundary"


def test_get_horrorfest_analytics_comparison_returns_payload(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_comparison",
        lambda *_args, **_kwargs: {
            "left_year": 2025,
            "right_year": 2024,
            "left_summary": {
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
            "right_summary": {
                "horrorfest_year": 2024,
                "watch_count": 203,
                "watch_days": 43,
                "new_watch_count": 125,
                "rewatch_count": 78,
                "total_runtime_seconds": 1227960,
                "total_runtime_hours": Decimal("341.10"),
                "average_watches_per_day": Decimal("4.72"),
                "average_runtime_hours_per_day": Decimal("7.93"),
                "average_runtime_minutes_per_watch": Decimal("100.80"),
                "average_rating_value": Decimal("7.46"),
                "rated_watch_count": 203,
                "first_watch_at": datetime.now(UTC),
                "latest_watch_at": datetime.now(UTC),
            },
            "delta": {
                "watch_count": 3,
                "watch_days": 0,
                "new_watch_count": 6,
                "rewatch_count": -3,
                "total_runtime_seconds": 17280,
                "total_runtime_hours": Decimal("4.80"),
                "average_watches_per_day": Decimal("0.07"),
                "average_runtime_hours_per_day": Decimal("0.11"),
                "average_runtime_minutes_per_watch": Decimal("-0.10"),
                "average_rating_value": Decimal("0.14"),
                "rated_watch_count": 3,
            },
            "source_rows": [
                {
                    "playback_source": "kodi",
                    "left_watch_count": 150,
                    "right_watch_count": 120,
                    "delta_watch_count": 30,
                    "left_total_runtime_hours": Decimal("250.00"),
                    "right_total_runtime_hours": Decimal("220.00"),
                    "delta_total_runtime_hours": Decimal("30.00"),
                }
            ],
            "rating_rows": [
                {
                    "rating_value": Decimal("8.00"),
                    "left_watch_count": 42,
                    "right_watch_count": 39,
                    "delta_watch_count": 3,
                }
            ],
            "repeated_title_rows": [
                {
                    "media_item_id": uuid4(),
                    "title": "In the Mouth of Madness",
                    "total_count": 7,
                    "left_year_count": 0,
                    "right_year_count": 1,
                    "delta_count": -1,
                }
            ],
        },
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/compare?left_year=2025&right_year=2024")

    assert response.status_code == 200
    payload = response.json()
    assert payload["left_year"] == 2025
    assert payload["delta"]["watch_count"] == 3
    assert payload["source_rows"][0]["playback_source"] == "kodi"


def test_get_horrorfest_repeated_titles_leaderboard_returns_payload(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_repeated_titles",
        lambda *_args, **_kwargs: {
            "years": [2025, 2024],
            "rows": [
                {
                    "media_item_id": uuid4(),
                    "title": "In the Mouth of Madness",
                    "total_count": 7,
                    "year_counts": {"2025": 0, "2024": 1},
                }
            ],
        },
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/leaderboards/repeated-titles")

    assert response.status_code == 200
    payload = response.json()
    assert payload["rows"][0]["total_count"] == 7


def test_get_horrorfest_curation_streaks_returns_payload(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_curation_streaks",
        lambda *_args, **_kwargs: [
            {
                "media_item_id": uuid4(),
                "title": "Halloween",
                "total_count": 4,
                "years_seen": 4,
                "first_year": 2021,
                "latest_year": 2025,
                "current_streak_length": 2,
                "longest_streak_length": 3,
                "streak_start_year": 2021,
                "streak_end_year": 2023,
                "gap_years": None,
                "gap_start_year": None,
                "gap_end_year": None,
                "years_since_last_seen": 0,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/curation/streaks")

    assert response.status_code == 200
    payload = response.json()
    assert payload["rows"][0]["title"] == "Halloween"
    assert payload["rows"][0]["longest_streak_length"] == 3


def test_get_horrorfest_curation_dormant_passes_window(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    captured = {}

    def fake_get(*_args, **kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_curation_dormant",
        fake_get,
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/curation/dormant?dormant_year_window=4")

    assert response.status_code == 200
    assert captured["dormant_year_window"] == 4


def test_export_horrorfest_analytics_years_returns_csv(monkeypatch) -> None:
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
    response = client.get("/api/v1/horrorfest/analytics/export/years")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=\"horrorfest_year_summary.csv\"" == response.headers["content-disposition"]
    assert "horrorfest_year,watch_count" in response.text


def test_export_horrorfest_comparison_returns_csv(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_comparison",
        lambda *_args, **_kwargs: {
            "left_year": 2025,
            "right_year": 2024,
            "left_summary": {
                "watch_count": 206,
                "watch_days": 43,
                "new_watch_count": 131,
                "rewatch_count": 75,
                "total_runtime_hours": Decimal("345.90"),
                "average_rating_value": Decimal("7.60"),
            },
            "right_summary": {
                "watch_count": 203,
                "watch_days": 43,
                "new_watch_count": 125,
                "rewatch_count": 78,
                "total_runtime_hours": Decimal("341.10"),
                "average_rating_value": Decimal("7.46"),
            },
            "delta": {
                "watch_count": 3,
                "watch_days": 0,
                "new_watch_count": 6,
                "rewatch_count": -3,
                "total_runtime_seconds": 0,
                "total_runtime_hours": Decimal("4.80"),
                "average_watches_per_day": Decimal("0.07"),
                "average_runtime_hours_per_day": Decimal("0.11"),
                "average_runtime_minutes_per_watch": Decimal("-0.10"),
                "average_rating_value": Decimal("0.14"),
                "rated_watch_count": 3,
            },
            "source_rows": [],
            "rating_rows": [],
            "repeated_title_rows": [],
        },
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/export/compare?left_year=2025&right_year=2024")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "section,metric,left_year,right_year,delta" in response.text


def test_export_horrorfest_curation_staples_returns_csv(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        HorrorfestService,
        "get_analytics_curation_staples",
        lambda *_args, **_kwargs: [
            {
                "media_item_id": uuid4(),
                "title": "Halloween",
                "total_count": 5,
                "years_seen": 5,
                "first_year": 2020,
                "latest_year": 2025,
                "current_streak_length": 2,
                "longest_streak_length": 3,
                "streak_start_year": 2020,
                "streak_end_year": 2022,
                "gap_years": None,
                "gap_start_year": None,
                "gap_end_year": None,
                "years_since_last_seen": 0,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/horrorfest/analytics/export/curation/staples")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="horrorfest_annual_staples.csv"'
    )
    assert "title,total_count,years_seen" in response.text
