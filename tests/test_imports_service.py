from datetime import UTC, datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.schemas.imports import ImportMode, ImportedWatchEvent, WatchEventImportRequest
from app.services.imports import WatchEventImportService


def _payload() -> WatchEventImportRequest:
    return WatchEventImportRequest(
        source="legacy_source_export",
        mode=ImportMode.bootstrap,
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
    assert result.error_count == 0


def test_run_import_partial_failure(monkeypatch) -> None:
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
        if calls["create"] == 2:
            raise ValueError("bad row")
        return None

    def fake_add_import_batch_error(_session: Session, **kwargs):
        calls["errors"] += 1
        assert kwargs["entity_ref"] == "evt-2"
        return None

    def fake_finish_import_batch(_session: Session, **kwargs):
        assert kwargs["watch_events_inserted"] == 1
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
    assert result.inserted_count == 1
    assert result.error_count == 1
    assert calls["errors"] == 1
