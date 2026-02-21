from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.import_batches import (
    ImportBatchConstraintError,
    ImportBatchNotFoundError,
    ImportBatchService,
)


class DummyImportBatch:
    def __init__(self, *, status: str = "running") -> None:
        self.import_batch_id = uuid4()
        self.source = "manual"
        self.source_detail = None
        self.started_at = datetime.now(UTC)
        self.finished_at = None
        self.status = status
        self.watch_events_inserted = 0
        self.media_items_inserted = 0
        self.media_versions_inserted = 0
        self.tags_added = 0
        self.errors_count = 0
        self.notes = None
        self.parameters = {}


def test_start_import_batch_returns_201(monkeypatch) -> None:
    batch = DummyImportBatch()

    def fake_start_import_batch(_session, **_kwargs):
        return batch

    monkeypatch.setattr(
        ImportBatchService, "start_import_batch", fake_start_import_batch
    )

    client = TestClient(app)
    response = client.post("/api/v1/import-batches", json={"source": "manual"})

    assert response.status_code == 201
    assert response.json()["status"] == "running"


def test_list_import_batches_returns_parameters(monkeypatch) -> None:
    batch = DummyImportBatch(status="completed")
    batch.parameters = {"mode": "incremental", "resume_from_latest": True}

    monkeypatch.setattr(
        ImportBatchService,
        "list_import_batches",
        lambda _session, **_kwargs: [batch],
    )

    client = TestClient(app)
    response = client.get("/api/v1/import-batches")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["parameters"]["mode"] == "incremental"
    assert payload[0]["parameters"]["resume_from_latest"] is True


def test_get_import_batch_not_found_returns_404(monkeypatch) -> None:
    def fake_get_import_batch(_session, **_kwargs):
        raise ImportBatchNotFoundError("missing")

    monkeypatch.setattr(ImportBatchService, "get_import_batch", fake_get_import_batch)

    client = TestClient(app)
    response = client.get(f"/api/v1/import-batches/{uuid4()}")

    assert response.status_code == 404


def test_finish_import_batch_constraint_error_returns_409(monkeypatch) -> None:
    def fake_finish_import_batch(_session, **_kwargs):
        raise ImportBatchConstraintError("Failed to finish import batch")

    monkeypatch.setattr(
        ImportBatchService,
        "finish_import_batch",
        fake_finish_import_batch,
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/import-batches/{uuid4()}/finish",
        json={"status": "completed"},
    )

    assert response.status_code == 409


def test_list_import_batch_errors_returns_rows(monkeypatch) -> None:
    class DummyImportBatchError:
        def __init__(self) -> None:
            self.import_batch_error_id = uuid4()
            self.import_batch_id = uuid4()
            self.occurred_at = datetime.now(UTC)
            self.severity = "error"
            self.entity_type = "watch_event"
            self.entity_ref = "evt-1"
            self.message = "bad payload"
            self.details = {"row_index": 4}

    monkeypatch.setattr(
        ImportBatchService,
        "list_import_batch_errors",
        lambda _session, **_kwargs: [DummyImportBatchError()],
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/import-batches/{uuid4()}/errors")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["message"] == "bad payload"


def test_list_import_batch_errors_not_found_returns_404(monkeypatch) -> None:
    def fake_list_import_batch_errors(_session, **_kwargs):
        raise ImportBatchNotFoundError("missing")

    monkeypatch.setattr(
        ImportBatchService,
        "list_import_batch_errors",
        fake_list_import_batch_errors,
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/import-batches/{uuid4()}/errors")

    assert response.status_code == 404
