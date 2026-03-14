from unittest.mock import Mock
from uuid import uuid4

from app.services.playback_events import PlaybackEventService


def test_list_playback_events_normalizes_filters_and_clamps_paging(monkeypatch) -> None:
    session = Mock()

    def fake_list_playback_events(_session, **kwargs):
        assert kwargs["playback_source"] == "kodi"
        assert kwargs["collector"] == "node_red"
        assert kwargs["session_key"] == "session-1"
        assert kwargs["event_type"] == "stop"
        assert kwargs["media_type"] == "movie"
        assert kwargs["limit"] == 100
        assert kwargs["offset"] == 0
        return []

    monkeypatch.setattr(
        "app.services.playback_events.playback_event_repository.list_playback_events",
        fake_list_playback_events,
    )

    PlaybackEventService.list_playback_events(
        session,
        user_id=uuid4(),
        playback_source=" kodi ",
        collector=" node_red ",
        session_key=" session-1 ",
        event_type=" stop ",
        media_type=" movie ",
        limit=500,
        offset=-10,
    )
