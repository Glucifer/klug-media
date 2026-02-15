from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.import_batches import (
    ImportBatchConstraintError,
    ImportBatchNotFoundError,
    ImportBatchService,
)


def test_start_import_batch_strips_source(monkeypatch) -> None:
    session = Mock()
    expected_batch = Mock()

    def fake_create_import_batch(_session, **kwargs):
        assert kwargs["source"] == "manual"
        return expected_batch

    monkeypatch.setattr(
        "app.services.import_batches.import_batch_repository.create_import_batch",
        fake_create_import_batch,
    )

    batch = ImportBatchService.start_import_batch(
        session,
        source=" manual ",
        source_detail=None,
        notes=None,
    )

    assert batch is expected_batch
    session.commit.assert_called_once()


def test_start_import_batch_integrity_error_maps(monkeypatch) -> None:
    session = Mock()

    def fake_create_import_batch(_session, **_kwargs):
        raise IntegrityError("insert", {}, Exception("dup"))

    monkeypatch.setattr(
        "app.services.import_batches.import_batch_repository.create_import_batch",
        fake_create_import_batch,
    )

    with pytest.raises(ImportBatchConstraintError):
        ImportBatchService.start_import_batch(
            session,
            source="manual",
            source_detail=None,
            notes=None,
        )


def test_finish_import_batch_not_found(monkeypatch) -> None:
    session = Mock()

    monkeypatch.setattr(
        "app.services.import_batches.import_batch_repository.get_import_batch",
        lambda _session, **_kwargs: None,
    )

    with pytest.raises(ImportBatchNotFoundError):
        ImportBatchService.finish_import_batch(
            session,
            import_batch_id=uuid4(),
            status="completed",
            watch_events_inserted=0,
            media_items_inserted=0,
            media_versions_inserted=0,
            tags_added=0,
            errors_count=0,
            notes=None,
        )
