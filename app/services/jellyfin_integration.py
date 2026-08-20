from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories import import_batches as import_batch_repository
from app.repositories import playback_events as playback_event_repository
from app.repositories import users as user_repository
from app.services.jellyfin import (
    JellyfinClient,
    JellyfinClientError,
    JellyfinConfigurationError,
)
from app.services.jellyfin_webhooks import JellyfinWebhookService
from app.services.users import UserService


@dataclass(frozen=True)
class JellyfinUserMapping:
    jellyfin_user_id: UUID
    jellyfin_username: str
    klug_user_id: UUID | None
    klug_username: str | None


@dataclass(frozen=True)
class JellyfinIntegrationStatus:
    configured: bool
    connected: bool
    connection_error: str | None
    mapped_user_count: int
    latest_webhook_at: datetime | None
    latest_webhook_decision: str | None
    latest_reconciliation_at: datetime | None
    latest_reconciliation_status: str | None


class JellyfinIntegrationService:
    @staticmethod
    def list_user_mappings(
        session: Session,
        *,
        client: JellyfinClient | None = None,
    ) -> list[JellyfinUserMapping]:
        jellyfin_users = (client or JellyfinClient.from_settings()).list_users()
        klug_users = UserService.list_users(session)
        mapped_by_id = {
            user.jellyfin_user_id: user
            for user in klug_users
            if user.jellyfin_user_id is not None
        }
        return [
            JellyfinUserMapping(
                jellyfin_user_id=jellyfin_user.user_id,
                jellyfin_username=jellyfin_user.name,
                klug_user_id=mapped_by_id[jellyfin_user.user_id].user_id
                if jellyfin_user.user_id in mapped_by_id
                else None,
                klug_username=mapped_by_id[jellyfin_user.user_id].username
                if jellyfin_user.user_id in mapped_by_id
                else None,
            )
            for jellyfin_user in jellyfin_users
        ]

    @staticmethod
    def get_status(
        session: Session,
        *,
        client: JellyfinClient | None = None,
    ) -> JellyfinIntegrationStatus:
        settings = get_settings()
        configured = bool(
            settings.klug_jellyfin_base_url and settings.klug_jellyfin_api_key
        )
        connected = False
        connection_error = None
        if configured:
            try:
                (client or JellyfinClient.from_settings()).list_users()
                connected = True
            except (JellyfinClientError, JellyfinConfigurationError) as exc:
                connection_error = str(exc)

        latest_webhook = (
            playback_event_repository.get_latest_playback_event_for_collector(
                session,
                collector=JellyfinWebhookService.COLLECTOR,
            )
        )
        latest_reconciliation = (
            import_batch_repository.get_latest_import_batch_for_source(
                session,
                source="jellyfin_reconcile",
                source_detail=None,
            )
        )
        return JellyfinIntegrationStatus(
            configured=configured,
            connected=connected,
            connection_error=connection_error,
            mapped_user_count=user_repository.count_mapped_jellyfin_users(session),
            latest_webhook_at=latest_webhook.occurred_at
            if latest_webhook is not None
            else None,
            latest_webhook_decision=latest_webhook.decision_status
            if latest_webhook is not None
            else None,
            latest_reconciliation_at=latest_reconciliation.finished_at
            if latest_reconciliation is not None
            else None,
            latest_reconciliation_status=latest_reconciliation.status
            if latest_reconciliation is not None
            else None,
        )
