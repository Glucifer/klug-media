from app.scripts import backfill_episode_shows
from app.services.show_backfill import ShowBackfillResult


def test_run_executes_service(monkeypatch) -> None:
    class DummySession:
        def close(self) -> None:
            return None

    monkeypatch.setattr(backfill_episode_shows, "SessionLocal", lambda: DummySession())

    captured: dict[str, object] = {}

    def fake_backfill(_session, *, dry_run: bool, limit: int | None):
        captured["dry_run"] = dry_run
        captured["limit"] = limit
        return ShowBackfillResult(
            scanned_count=5,
            linked_count=5,
            shows_created_count=2,
            dry_run=True,
        )

    monkeypatch.setattr(
        backfill_episode_shows.ShowBackfillService,
        "backfill_episode_show_links",
        fake_backfill,
    )

    exit_code = backfill_episode_shows.run(["--dry-run", "--limit", "10"])
    assert exit_code == 0
    assert captured["dry_run"] is True
    assert captured["limit"] == 10


def test_run_invalid_limit_returns_2() -> None:
    exit_code = backfill_episode_shows.run(["--limit", "0"])
    assert exit_code == 2


def test_run_returns_1_when_service_raises(monkeypatch) -> None:
    class DummySession:
        def close(self) -> None:
            return None

    monkeypatch.setattr(backfill_episode_shows, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        backfill_episode_shows.ShowBackfillService,
        "backfill_episode_show_links",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("boom")),
    )

    exit_code = backfill_episode_shows.run([])
    assert exit_code == 1
