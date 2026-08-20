from datetime import UTC, datetime
from uuid import UUID

from app.services.jellyfin import JellyfinClient, normalize_jellyfin_item_id


USER_ID = UUID("11111111-1111-1111-1111-111111111111")
ITEM_ID = "22222222222222222222222222222222"


def test_normalize_jellyfin_item_id() -> None:
    assert normalize_jellyfin_item_id("22222222-2222-2222-2222-222222222222") == ITEM_ID


def test_list_users_skips_invalid_rows(monkeypatch) -> None:
    client = JellyfinClient(
        base_url="http://jellyfin", api_key="secret", timeout_seconds=5
    )
    monkeypatch.setattr(
        client,
        "_request_json_array",
        lambda _path: [
            {"Id": USER_ID.hex, "Name": "Travis"},
            {"Id": "invalid", "Name": "Ignored"},
        ],
    )

    users = client.list_users()

    assert len(users) == 1
    assert users[0].user_id == USER_ID
    assert users[0].name == "Travis"


def test_list_played_items_paginates_and_sends_cursor(monkeypatch) -> None:
    client = JellyfinClient(
        base_url="http://jellyfin", api_key="secret", timeout_seconds=5
    )
    calls: list[dict[str, str]] = []
    raw_item = {
        "Id": ITEM_ID,
        "Type": "Movie",
        "Name": "Alien",
        "ProductionYear": 1979,
        "RunTimeTicks": 7_020_000_0000,
        "ProviderIds": {"Tmdb": "348", "Imdb": "tt0078748"},
        "UserData": {
            "Played": True,
            "PlayCount": 2,
            "LastPlayedDate": "2026-08-20T12:00:00Z",
        },
    }

    def fake_request(_path: str, *, params: dict[str, str]):
        calls.append(params)
        if len(calls) == 1:
            return {"Items": [raw_item] * 200}
        return {"Items": []}

    monkeypatch.setattr(client, "_request_json", fake_request)

    items = client.list_played_items(
        user_id=USER_ID,
        changed_since=datetime(2026, 5, 20, tzinfo=UTC),
    )

    assert len(items) == 200
    assert items[0].source_item_id == ITEM_ID
    assert items[0].played is True
    assert items[0].play_count == 2
    assert items[0].last_played_at == datetime(2026, 8, 20, 12, tzinfo=UTC)
    assert calls[0]["minDateLastSavedForUser"] == "2026-05-20T00:00:00Z"
    assert calls[1]["startIndex"] == "200"
