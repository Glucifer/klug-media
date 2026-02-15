from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.schemas.imports import (
    ImportMode,
    ImportedWatchEvent,
    LegacySourceWatchEventImportRequest,
    LegacySourceWatchEventRow,
    WatchEventImportRequest,
)
from app.services.imports import WatchEventImportService
from app.services.watch_events import WatchEventDuplicateError


def _payload(*, dry_run: bool = False) -> WatchEventImportRequest:
    return WatchEventImportRequest(
        source="legacy_source_export",
        mode=ImportMode.bootstrap,
        dry_run=dry_run,
        rejected_before_import=1,
        events=[
            ImportedWatchEvent(
                user_id=uuid4(),
                media_item_id=uuid4(),
                watched_at=datetime.now(UTC),
                playback_source="jellyfin",
                source_event_id="evt-1",
            ),
            ImportedWatchEvent(
                user_id=uuid4(),
                media_item_id=uuid4(),
                watched_at=datetime.now(UTC),
                playback_source="jellyfin",
                source_event_id="evt-2",
            ),
        ],
    )


def test_run_import_all_success(monkeypatch) -> None:
    session_obj = object()
    batch_id = uuid4()

    class DummyBatch:
        def __init__(self, import_batch_id: UUID, status: str = "running") -> None:
            self.import_batch_id = import_batch_id
            self.status = status

    def fake_start_import_batch(_session: Session, **_kwargs):
        assert _session is session_obj
        return DummyBatch(batch_id)

    def fake_create_watch_event(_session: Session, **_kwargs):
        assert _session is session_obj
        return None

    def fake_add_import_batch_error(_session: Session, **_kwargs):
        raise AssertionError("No errors expected")

    def fake_finish_import_batch(_session: Session, **kwargs):
        assert kwargs["watch_events_inserted"] == 2
        assert kwargs["errors_count"] == 0
        return DummyBatch(batch_id, status="completed")

    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.start_import_batch",
        fake_start_import_batch,
    )
    monkeypatch.setattr(
        "app.services.imports.WatchEventService.create_watch_event",
        fake_create_watch_event,
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.add_import_batch_error",
        fake_add_import_batch_error,
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.finish_import_batch",
        fake_finish_import_batch,
    )

    result = WatchEventImportService.run_import(session_obj, payload=_payload())

    assert result.status == "completed"
    assert result.inserted_count == 2
    assert result.skipped_count == 0
    assert result.error_count == 0
    assert result.rejected_before_import == 1


def test_run_import_partial_failure_and_duplicate_skip(monkeypatch) -> None:
    session_obj = object()
    batch_id = uuid4()

    class DummyBatch:
        def __init__(self, import_batch_id: UUID, status: str = "running") -> None:
            self.import_batch_id = import_batch_id
            self.status = status

    calls = {"create": 0, "errors": 0}

    def fake_start_import_batch(_session: Session, **_kwargs):
        return DummyBatch(batch_id)

    def fake_create_watch_event(_session: Session, **_kwargs):
        calls["create"] += 1
        if calls["create"] == 1:
            raise WatchEventDuplicateError("Watch event already exists")
        if calls["create"] == 2:
            raise ValueError("bad row")
        return None

    def fake_add_import_batch_error(_session: Session, **kwargs):
        calls["errors"] += 1
        assert kwargs["entity_ref"] == "evt-2"
        return None

    def fake_finish_import_batch(_session: Session, **kwargs):
        assert kwargs["watch_events_inserted"] == 0
        assert kwargs["errors_count"] == 1
        return DummyBatch(batch_id, status="completed_with_errors")

    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.start_import_batch",
        fake_start_import_batch,
    )
    monkeypatch.setattr(
        "app.services.imports.WatchEventService.create_watch_event",
        fake_create_watch_event,
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.add_import_batch_error",
        fake_add_import_batch_error,
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.finish_import_batch",
        fake_finish_import_batch,
    )

    result = WatchEventImportService.run_import(session_obj, payload=_payload())

    assert result.status == "completed_with_errors"
    assert result.inserted_count == 0
    assert result.skipped_count == 1
    assert result.error_count == 1
    assert result.rejected_before_import == 1
    assert calls["errors"] == 1


def test_run_import_dry_run_skips_db_writes(monkeypatch) -> None:
    session_obj = object()

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("DB write should not be called for dry_run")

    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.start_import_batch",
        fail_if_called,
    )

    result = WatchEventImportService.run_import(
        session_obj,
        payload=_payload(dry_run=True),
    )

    assert result.status == "dry_run"
    assert result.dry_run is True
    assert result.inserted_count == 2
    assert result.skipped_count == 0
    assert result.error_count == 0
    assert result.rejected_before_import == 1


def test_run_legacy_source_import_maps_rows(monkeypatch) -> None:
    session_obj = object()

    payload = LegacySourceWatchEventImportRequest(
        mode=ImportMode.incremental,
        dry_run=True,
        rejected_before_import=9,
        rows=[
            LegacySourceWatchEventRow(
                user_id=uuid4(),
                media_item_id=uuid4(),
                watched_at=datetime.now(UTC),
                player="jellyfin",
                source_event_id="legacy-evt-1",
            )
        ],
    )

    captured = {}

    def fake_run_import(_session: Session, *, payload: WatchEventImportRequest):
        captured["source"] = payload.source
        captured["mode"] = payload.mode
        captured["dry_run"] = payload.dry_run
        captured["rejected_before_import"] = payload.rejected_before_import
        captured["playback_source"] = payload.events[0].playback_source
        return type(
            "Result",
            (),
            {
                "import_batch_id": UUID("00000000-0000-0000-0000-000000000000"),
                "status": "dry_run",
                "dry_run": True,
                "processed_count": 1,
                "inserted_count": 1,
                "skipped_count": 0,
                "error_count": 0,
            },
        )()

    monkeypatch.setattr(
        "app.services.imports.WatchEventImportService.run_import",
        fake_run_import,
    )

    WatchEventImportService.run_legacy_source_import(session_obj, payload=payload)

    assert captured["source"] == "legacy_source_export"
    assert captured["mode"] == ImportMode.incremental
    assert captured["dry_run"] is True
    assert captured["playback_source"] == "jellyfin"
    assert captured["rejected_before_import"] == 9


def test_run_incremental_resume_skips_rows_before_cursor(monkeypatch) -> None:
    session_obj = object()
    batch_id = uuid4()

    class DummyBatch:
        def __init__(
            self,
            import_batch_id: UUID,
            status: str = "running",
            parameters: dict | None = None,
        ) -> None:
            self.import_batch_id = import_batch_id
            self.status = status
            self.parameters = parameters or {}

    cursor = {
        "watched_at": "2025-01-01T12:00:00+00:00",
        "source_event_id": "evt-2",
    }
    current_batch = DummyBatch(batch_id)

    payload = WatchEventImportRequest(
        source="legacy_source_export",
        mode=ImportMode.incremental,
        resume_from_latest=True,
        source_detail="incremental",
        rejected_before_import=2,
        events=[
            ImportedWatchEvent(
                user_id=uuid4(),
                media_item_id=uuid4(),
                watched_at=datetime.fromisoformat("2025-01-01T11:00:00+00:00"),
                playback_source="jellyfin",
                source_event_id="evt-1",
            ),
            ImportedWatchEvent(
                user_id=uuid4(),
                media_item_id=uuid4(),
                watched_at=datetime.fromisoformat("2025-01-01T12:00:00+00:00"),
                playback_source="jellyfin",
                source_event_id="evt-2",
            ),
            ImportedWatchEvent(
                user_id=uuid4(),
                media_item_id=uuid4(),
                watched_at=datetime.fromisoformat("2025-01-01T13:00:00+00:00"),
                playback_source="jellyfin",
                source_event_id="evt-3",
            ),
        ],
    )

    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.get_latest_import_batch_for_source",
        lambda *_args, **_kwargs: DummyBatch(uuid4(), parameters={"cursor": cursor}),
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: current_batch,
    )
    monkeypatch.setattr(
        "app.services.imports.WatchEventService.source_event_exists",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "app.services.imports.WatchEventService.create_watch_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.add_import_batch_error",
        lambda *_args, **_kwargs: None,
    )

    def fake_finish_import_batch(_session: Session, **kwargs):
        assert kwargs["watch_events_inserted"] == 1
        assert kwargs["errors_count"] == 0
        assert kwargs["parameters_patch"]["cursor_before"] == cursor
        assert kwargs["parameters_patch"]["cursor"]["source_event_id"] == "evt-3"
        return DummyBatch(batch_id, status="completed")

    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.finish_import_batch",
        fake_finish_import_batch,
    )

    result = WatchEventImportService.run_import(session_obj, payload=payload)
    assert result.inserted_count == 1
    assert result.skipped_count == 2
    assert result.error_count == 0
    assert result.rejected_before_import == 2


def test_run_incremental_skips_existing_source_event_id(monkeypatch) -> None:
    session_obj = object()
    batch_id = uuid4()

    class DummyBatch:
        def __init__(self, import_batch_id: UUID, status: str = "running") -> None:
            self.import_batch_id = import_batch_id
            self.status = status
            self.parameters = {}

    payload = WatchEventImportRequest(
        source="legacy_source_export",
        mode=ImportMode.incremental,
        source_detail="incremental",
        rejected_before_import=3,
        events=[
            ImportedWatchEvent(
                user_id=uuid4(),
                media_item_id=uuid4(),
                watched_at=datetime.now(UTC),
                playback_source="jellyfin",
                source_event_id="evt-1",
            )
        ],
    )

    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.get_latest_import_batch_for_source",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.start_import_batch",
        lambda *_args, **_kwargs: DummyBatch(batch_id),
    )
    monkeypatch.setattr(
        "app.services.imports.WatchEventService.source_event_exists",
        lambda *_args, **_kwargs: True,
    )
    monkeypatch.setattr(
        "app.services.imports.WatchEventService.create_watch_event",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("create_watch_event should not be called")
        ),
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.add_import_batch_error",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.imports.ImportBatchService.finish_import_batch",
        lambda *_args, **_kwargs: DummyBatch(batch_id, status="completed"),
    )

    result = WatchEventImportService.run_import(session_obj, payload=payload)
    assert result.inserted_count == 0
    assert result.skipped_count == 1
    assert result.rejected_before_import == 3
