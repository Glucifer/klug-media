"""Add decision outcome fields to playback events."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0006_add_playback_event_decision_fields"
down_revision = "0005_add_playback_event_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "playback_event",
        sa.Column("decision_status", sa.String(), nullable=True),
        schema="app",
    )
    op.add_column(
        "playback_event",
        sa.Column("decision_reason", sa.String(), nullable=True),
        schema="app",
    )
    op.add_column(
        "playback_event",
        sa.Column("watch_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="app",
    )
    op.create_foreign_key(
        "fk_playback_event_watch_id",
        "playback_event",
        "watch_event",
        ["watch_id"],
        ["watch_id"],
        source_schema="app",
        referent_schema="app",
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_playback_event_watch_id",
        "playback_event",
        schema="app",
        type_="foreignkey",
    )
    op.drop_column("playback_event", "watch_id", schema="app")
    op.drop_column("playback_event", "decision_reason", schema="app")
    op.drop_column("playback_event", "decision_status", schema="app")
