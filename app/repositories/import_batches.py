from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.models.entities import ImportBatch, ImportBatchError


def list_import_batches(session: Session, *, limit: int) -> list[ImportBatch]:
    statement = select(ImportBatch).order_by(ImportBatch.started_at.desc()).limit(limit)
    return list(session.scalars(statement))


def get_import_batch(session: Session, *, import_batch_id: UUID) -> ImportBatch | None:
    statement = select(ImportBatch).where(
        ImportBatch.import_batch_id == import_batch_id
    )
    return session.scalar(statement)


def create_import_batch(
    session: Session,
    *,
    source: str,
    source_detail: str | None,
    notes: str | None,
    parameters: dict | None = None,
) -> ImportBatch:
    batch = ImportBatch(
        source=source,
        source_detail=source_detail,
        notes=notes,
        status="running",
        parameters=parameters or {},
    )
    session.add(batch)
    session.flush()
    session.refresh(batch)
    return batch


def finish_import_batch(
    session: Session,
    *,
    import_batch: ImportBatch,
    status: str,
    watch_events_inserted: int,
    media_items_inserted: int,
    media_versions_inserted: int,
    tags_added: int,
    errors_count: int,
    notes: str | None,
    parameters_patch: dict | None = None,
) -> ImportBatch:
    import_batch.status = status
    import_batch.finished_at = datetime.now(UTC)
    import_batch.watch_events_inserted = watch_events_inserted
    import_batch.media_items_inserted = media_items_inserted
    import_batch.media_versions_inserted = media_versions_inserted
    import_batch.tags_added = tags_added
    import_batch.errors_count = errors_count
    import_batch.notes = notes
    if parameters_patch:
        merged_parameters = dict(import_batch.parameters or {})
        merged_parameters.update(parameters_patch)
        import_batch.parameters = merged_parameters

    session.flush()
    session.refresh(import_batch)
    return import_batch


def list_import_batch_errors(
    session: Session,
    *,
    import_batch_id: UUID,
    limit: int,
) -> list[ImportBatchError]:
    statement = (
        select(ImportBatchError)
        .where(ImportBatchError.import_batch_id == import_batch_id)
        .order_by(ImportBatchError.occurred_at.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))


def create_import_batch_error(
    session: Session,
    *,
    import_batch: ImportBatch,
    severity: str,
    entity_type: str | None,
    entity_ref: str | None,
    message: str,
    details: dict,
) -> ImportBatchError:
    error = ImportBatchError(
        import_batch_id=import_batch.import_batch_id,
        severity=severity,
        entity_type=entity_type,
        entity_ref=entity_ref,
        message=message,
        details=details,
    )
    session.add(error)
    import_batch.errors_count = (import_batch.errors_count or 0) + 1
    session.flush()
    session.refresh(error)
    return error


def get_latest_import_batch_for_source(
    session: Session,
    *,
    source: str,
    source_detail: str | None,
) -> ImportBatch | None:
    statement: Select[tuple[ImportBatch]] = select(ImportBatch).where(
        ImportBatch.source == source
    )
    if source_detail is not None:
        statement = statement.where(ImportBatch.source_detail == source_detail)

    statement = statement.order_by(ImportBatch.started_at.desc()).limit(1)
    return session.scalar(statement)
