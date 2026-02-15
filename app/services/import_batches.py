from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.entities import ImportBatch, ImportBatchError
from app.repositories import import_batches as import_batch_repository


class ImportBatchNotFoundError(Exception):
    """Raised when an import batch does not exist."""


class ImportBatchConstraintError(Exception):
    """Raised when import batch persistence fails constraints."""


class ImportBatchService:
    @staticmethod
    def list_import_batches(session: Session, *, limit: int) -> list[ImportBatch]:
        safe_limit = max(1, min(limit, 100))
        return import_batch_repository.list_import_batches(session, limit=safe_limit)

    @staticmethod
    def get_import_batch(session: Session, *, import_batch_id: UUID) -> ImportBatch:
        batch = import_batch_repository.get_import_batch(
            session, import_batch_id=import_batch_id
        )
        if batch is None:
            raise ImportBatchNotFoundError(str(import_batch_id))
        return batch

    @staticmethod
    def start_import_batch(
        session: Session,
        *,
        source: str,
        source_detail: str | None,
        notes: str | None,
    ) -> ImportBatch:
        normalized_source = source.strip()
        normalized_source_detail = source_detail.strip() if source_detail else None

        if not normalized_source:
            raise ValueError("source must not be empty")

        try:
            batch = import_batch_repository.create_import_batch(
                session,
                source=normalized_source,
                source_detail=normalized_source_detail,
                notes=notes,
            )
            session.commit()
            return batch
        except IntegrityError as exc:
            session.rollback()
            raise ImportBatchConstraintError("Failed to start import batch") from exc

    @staticmethod
    def finish_import_batch(
        session: Session,
        *,
        import_batch_id: UUID,
        status: str,
        watch_events_inserted: int,
        media_items_inserted: int,
        media_versions_inserted: int,
        tags_added: int,
        errors_count: int,
        notes: str | None,
    ) -> ImportBatch:
        normalized_status = status.strip()
        if not normalized_status:
            raise ValueError("status must not be empty")

        batch = import_batch_repository.get_import_batch(
            session, import_batch_id=import_batch_id
        )
        if batch is None:
            raise ImportBatchNotFoundError(str(import_batch_id))

        try:
            updated_batch = import_batch_repository.finish_import_batch(
                session,
                import_batch=batch,
                status=normalized_status,
                watch_events_inserted=watch_events_inserted,
                media_items_inserted=media_items_inserted,
                media_versions_inserted=media_versions_inserted,
                tags_added=tags_added,
                errors_count=errors_count,
                notes=notes,
            )
            session.commit()
            return updated_batch
        except IntegrityError as exc:
            session.rollback()
            raise ImportBatchConstraintError("Failed to finish import batch") from exc

    @staticmethod
    def list_import_batch_errors(
        session: Session,
        *,
        import_batch_id: UUID,
        limit: int,
    ) -> list[ImportBatchError]:
        batch = import_batch_repository.get_import_batch(
            session, import_batch_id=import_batch_id
        )
        if batch is None:
            raise ImportBatchNotFoundError(str(import_batch_id))

        safe_limit = max(1, min(limit, 100))
        return import_batch_repository.list_import_batch_errors(
            session,
            import_batch_id=import_batch_id,
            limit=safe_limit,
        )

    @staticmethod
    def add_import_batch_error(
        session: Session,
        *,
        import_batch_id: UUID,
        severity: str,
        entity_type: str | None,
        entity_ref: str | None,
        message: str,
        details: dict,
    ) -> ImportBatchError:
        normalized_severity = severity.strip()
        normalized_message = message.strip()
        normalized_entity_type = entity_type.strip() if entity_type else None
        normalized_entity_ref = entity_ref.strip() if entity_ref else None

        if not normalized_severity:
            raise ValueError("severity must not be empty")
        if not normalized_message:
            raise ValueError("message must not be empty")

        batch = import_batch_repository.get_import_batch(
            session, import_batch_id=import_batch_id
        )
        if batch is None:
            raise ImportBatchNotFoundError(str(import_batch_id))

        try:
            error = import_batch_repository.create_import_batch_error(
                session,
                import_batch=batch,
                severity=normalized_severity,
                entity_type=normalized_entity_type,
                entity_ref=normalized_entity_ref,
                message=normalized_message,
                details=details,
            )
            session.commit()
            return error
        except IntegrityError as exc:
            session.rollback()
            raise ImportBatchConstraintError(
                "Failed to add import batch error"
            ) from exc
