"""Add unique partial index for watch_event source event id."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_watch_event_source_event_unique"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

APP_SCHEMA = "app"


def upgrade() -> None:
    op.create_index(
        "ux_watch_event_source_event",
        "watch_event",
        ["playback_source", "source_event_id"],
        unique=True,
        schema=APP_SCHEMA,
        postgresql_where=sa.text("source_event_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ux_watch_event_source_event", table_name="watch_event", schema=APP_SCHEMA
    )
