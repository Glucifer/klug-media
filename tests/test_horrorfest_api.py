from datetime import UTC, datetime
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
