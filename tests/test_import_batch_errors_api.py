from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.import_batches import ImportBatchNotFoundError, ImportBatchService


class DummyImportBatchError:
    def __init__(self, *, import_batch_id=None) -> None:
        self.import_batch_error_id = uuid4()
        self.import_batch_id = import_batch_id or uuid4()
        self.occurred_at = datetime.now(UTC)
        self.severity = "error"
        self.entity_type = "watch_event"
        self.entity_ref = "evt-1"
        self.message = "Something failed"
        self.details = {"reason": "duplicate"}


def test_list_import_batch_errors_returns_items(monkeypatch) -> None:
    import_batch_id = uuid4()
    expected_error = DummyImportBatchError(import_batch_id=import_batch_id)

    def fake_list_import_batch_errors(_session, **kwargs):
        assert kwargs["import_batch_id"] == import_batch_id
        return [expected_error]

    monkeypatch.setattr(
        ImportBatchService,
        "list_import_batch_errors",
        fake_list_import_batch_errors,
    )

    client = TestClient(app)
    response = client.get(f"/api/v1/import-batches/{import_batch_id}/errors")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["message"] == "Something failed"


def test_add_import_batch_error_returns_201(monkeypatch) -> None:
    import_batch_id = uuid4()
    expected_error = DummyImportBatchError(import_batch_id=import_batch_id)

    def fake_add_import_batch_error(_session, **kwargs):
        assert kwargs["import_batch_id"] == import_batch_id
        return expected_error

    monkeypatch.setattr(
        ImportBatchService,
        "add_import_batch_error",
        fake_add_import_batch_error,
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/import-batches/{import_batch_id}/errors",
        json={
            "severity": "error",
            "message": "Something failed",
            "details": {"reason": "duplicate"},
        },
    )

    assert response.status_code == 201
    assert response.json()["severity"] == "error"


def test_add_import_batch_error_not_found_returns_404(monkeypatch) -> None:
    def fake_add_import_batch_error(_session, **_kwargs):
        raise ImportBatchNotFoundError("missing")

    monkeypatch.setattr(
        ImportBatchService,
        "add_import_batch_error",
        fake_add_import_batch_error,
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/import-batches/{uuid4()}/errors",
        json={"severity": "error", "message": "failed", "details": {}},
    )

    assert response.status_code == 404
