from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.stats import StatsService


def _set_permissive_auth(monkeypatch) -> None:
    monkeypatch.setenv("KLUG_API_KEY", "")
    monkeypatch.setenv("KLUG_API_AUTH_MODE", "write")
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("KLUG_SESSION_PASSWORD", "")
    monkeypatch.setenv("KLUG_SESSION_SECRET", "")
    get_settings.cache_clear()


def test_stats_summary_endpoint_returns_payload(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        StatsService,
        "get_summary",
        lambda *_args, **_kwargs: {
            "user_id": None,
            "total_active_watches": 10,
            "total_completed_watches": 8,
            "total_rewatches": 2,
            "total_watch_time_seconds": 36000,
            "total_watch_time_hours": Decimal("10.00"),
            "movie_watch_count": 4,
            "episode_watch_count": 6,
            "average_rating_value": Decimal("8.50"),
            "unrated_completed_watch_count": 3,
        },
    )
    client = TestClient(app)
    response = client.get("/api/v1/stats/summary")
    assert response.status_code == 200
    assert response.json()["total_active_watches"] == 10


def test_stats_monthly_endpoint_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        StatsService,
        "list_monthly",
        lambda *_args, **_kwargs: [
            {
                "user_id": None,
                "year": 2026,
                "month": 4,
                "watch_count": 5,
                "movie_count": 2,
                "episode_count": 3,
                "rewatch_count": 1,
                "rated_watch_count": 4,
                "total_runtime_seconds": 18000,
                "average_rating_value": Decimal("7.75"),
            }
        ],
    )
    client = TestClient(app)
    response = client.get("/api/v1/stats/monthly")
    assert response.status_code == 200
    assert response.json()[0]["month"] == 4


def test_stats_horrorfest_endpoint_returns_rows(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    monkeypatch.setattr(
        StatsService,
        "list_horrorfest",
        lambda *_args, **_kwargs: [
            {
                "user_id": None,
                "horrorfest_year": 2026,
                "entry_count": 12,
                "total_runtime_seconds": 43200,
                "total_runtime_hours": Decimal("12.00"),
                "average_rating_value": Decimal("8.10"),
                "rated_entry_count": 10,
                "rewatch_count": 2,
                "first_watch_at": datetime.now(UTC),
                "latest_watch_at": datetime.now(UTC),
            }
        ],
    )
    client = TestClient(app)
    response = client.get("/api/v1/stats/horrorfest")
    assert response.status_code == 200
    assert response.json()[0]["entry_count"] == 12


def test_stats_endpoints_forward_user_id(monkeypatch) -> None:
    _set_permissive_auth(monkeypatch)
    user_id = uuid4()
    captured = {}

    def fake_summary(_session, *, user_id):
        captured["user_id"] = user_id
        return {
            "user_id": user_id,
            "total_active_watches": 0,
            "total_completed_watches": 0,
            "total_rewatches": 0,
            "total_watch_time_seconds": 0,
            "total_watch_time_hours": Decimal("0.00"),
            "movie_watch_count": 0,
            "episode_watch_count": 0,
            "average_rating_value": None,
            "unrated_completed_watch_count": 0,
        }

    monkeypatch.setattr(StatsService, "get_summary", fake_summary)
    monkeypatch.setattr(StatsService, "list_monthly", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(StatsService, "list_horrorfest", lambda *_args, **_kwargs: [])

    client = TestClient(app)
    response = client.get(f"/api/v1/stats/summary?user_id={user_id}")
    assert response.status_code == 200
    assert captured["user_id"] == user_id
