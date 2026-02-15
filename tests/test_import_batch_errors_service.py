from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.import_batches import (
    ImportBatchConstraintError,
    ImportBatchNotFoundError,
    ImportBatchService,
)


def test_add_import_batch_error_strips_fields(monkeypatch) -> None:
    session = Mock()
    batch = Mock()
    expected_error = Mock()

    monkeypatch.setattr(
        "app.services.import_batches.import_batch_repository.get_import_batch",
        lambda _session, **_kwargs: batch,
    )

    def fake_create_import_batch_error(_session, **kwargs):
        assert kwargs["severity"] == "warning"
        assert kwargs["entity_type"] == "watch_event"
        assert kwargs["entity_ref"] == "evt-1"
        assert kwargs["message"] == "bad payload"
        return expected_error

    monkeypatch.setattr(
        "app.services.import_batches.import_batch_repository.create_import_batch_error",
        fake_create_import_batch_error,
    )

    error = ImportBatchService.add_import_batch_error(
        session,
        import_batch_id=uuid4(),
        severity=" warning ",
        entity_type=" watch_event ",
        entity_ref=" evt-1 ",
        message=" bad payload ",
        details={},
    )

    assert error is expected_error
    session.commit.assert_called_once()


def test_add_import_batch_error_not_found(monkeypatch) -> None:
    session = Mock()

    monkeypatch.setattr(
        "app.services.import_batches.import_batch_repository.get_import_batch",
        lambda _session, **_kwargs: None,
    )

    with pytest.raises(ImportBatchNotFoundError):
        ImportBatchService.add_import_batch_error(
            session,
            import_batch_id=uuid4(),
            severity="error",
            entity_type=None,
            entity_ref=None,
            message="failed",
            details={},
        )


def test_add_import_batch_error_integrity_error_maps(monkeypatch) -> None:
    session = Mock()
    batch = Mock()

    monkeypatch.setattr(
        "app.services.import_batches.import_batch_repository.get_import_batch",
        lambda _session, **_kwargs: batch,
    )

    def fake_create_import_batch_error(_session, **_kwargs):
        raise IntegrityError("insert", {}, Exception("constraint"))

    monkeypatch.setattr(
        "app.services.import_batches.import_batch_repository.create_import_batch_error",
        fake_create_import_batch_error,
    )

    with pytest.raises(ImportBatchConstraintError):
        ImportBatchService.add_import_batch_error(
            session,
            import_batch_id=uuid4(),
            severity="error",
            entity_type=None,
            entity_ref=None,
            message="failed",
            details={},
        )

    session.rollback.assert_called_once()
