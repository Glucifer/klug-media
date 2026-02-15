from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import ImportBatch


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
) -> ImportBatch:
    batch = ImportBatch(
        source=source,
        source_detail=source_detail,
        notes=notes,
        status="running",
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
) -> ImportBatch:
    import_batch.status = status
    import_batch.finished_at = datetime.now(UTC)
    import_batch.watch_events_inserted = watch_events_inserted
    import_batch.media_items_inserted = media_items_inserted
    import_batch.media_versions_inserted = media_versions_inserted
    import_batch.tags_added = tags_added
    import_batch.errors_count = errors_count
    import_batch.notes = notes

    session.flush()
    session.refresh(import_batch)
    return import_batch
