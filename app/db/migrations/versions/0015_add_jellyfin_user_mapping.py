"""Add Jellyfin user mapping and deterministic media item lookup."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0015_add_jellyfin_user_mapping"
down_revision = "0014_add_collection_entry_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "jellyfin_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema="app",
    )
    op.create_index(
        "ux_users_jellyfin_user_id",
        "users",
        ["jellyfin_user_id"],
        unique=True,
        schema="app",
        postgresql_where=sa.text("jellyfin_user_id IS NOT NULL"),
    )
    op.create_index(
        "ux_media_item_jellyfin_item_id",
        "media_item",
        ["jellyfin_item_id"],
        unique=True,
        schema="app",
        postgresql_where=sa.text("jellyfin_item_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ux_media_item_jellyfin_item_id",
        table_name="media_item",
        schema="app",
    )
    op.drop_index(
        "ux_users_jellyfin_user_id",
        table_name="users",
        schema="app",
    )
    op.drop_column("users", "jellyfin_user_id", schema="app")
