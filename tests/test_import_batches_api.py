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
