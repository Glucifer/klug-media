from uuid import uuid4

from app.services.scrobble_activity import ScrobbleActivityService


def test_list_scrobble_activity_normalizes_and_clamps(monkeypatch) -> None:
    session = object()
    called: dict[str, object] = {}

    def fake_list_scrobble_activity(_session, **kwargs):
        called.update(kwargs)
        assert _session is session
        return []

    monkeypatch.setattr(
        "app.services.scrobble_activity.scrobble_activity_repository.list_scrobble_activity",
        fake_list_scrobble_activity,
    )

    ScrobbleActivityService.list_scrobble_activity(
        session,
        user_id=uuid4(),
        collector=" node_red ",
        playback_source=" kodi ",
        decision_status=" watch_event_created ",
        event_type=" stop ",
        media_type="movie",
        occurred_after=None,
        occurred_before=None,
        only_unmatched=True,
        only_with_watch=False,
        limit=1000,
        offset=-5,
    )

    assert called["collector"] == "node_red"
    assert called["playback_source"] == "kodi"
    assert called["decision_status"] == "watch_event_created"
    assert called["event_type"] == "stop"
    assert called["media_type"] == "movie"
    assert called["limit"] == 100
    assert called["offset"] == 0
    assert called["only_unmatched"] is True
