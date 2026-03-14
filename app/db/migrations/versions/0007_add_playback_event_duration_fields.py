"""Add duration fields to playback events."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0007_add_playback_event_duration_fields"
down_revision = "0006_add_playback_event_decision_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "playback_event",
        sa.Column("total_seconds", sa.Integer(), nullable=True),
        schema="app",
    )
    op.add_column(
        "playback_event",
        sa.Column("watched_seconds", sa.Integer(), nullable=True),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("playback_event", "watched_seconds", schema="app")
    op.drop_column("playback_event", "total_seconds", schema="app")
