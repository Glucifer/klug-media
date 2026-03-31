"""Add provenance fields to watch events."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0008_add_watch_event_origin_fields"
down_revision = "0007_add_playback_event_duration_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "watch_event",
        sa.Column(
            "origin_kind",
            sa.String(),
            server_default=sa.text("'manual_entry'::text"),
            nullable=False,
        ),
        schema="app",
    )
    op.add_column(
        "watch_event",
        sa.Column("origin_playback_event_id", sa.UUID(), nullable=True),
        schema="app",
    )
    op.create_foreign_key(
        "watch_event_origin_playback_event_id_fkey",
        "watch_event",
        "playback_event",
        ["origin_playback_event_id"],
        ["playback_event_id"],
        source_schema="app",
        referent_schema="app",
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_watch_event_origin_playback",
        "watch_event",
        ["origin_playback_event_id"],
        unique=False,
        schema="app",
    )

    op.execute(
        """
        UPDATE app.watch_event AS we
        SET
            origin_kind = 'manual_import'
        WHERE we.import_batch_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE app.watch_event AS we
        SET
            origin_kind = 'live_playback',
            origin_playback_event_id = pe.playback_event_id
        FROM app.playback_event AS pe
        WHERE pe.watch_id = we.watch_id
        """
    )


def downgrade() -> None:
    op.drop_index("ix_watch_event_origin_playback", table_name="watch_event", schema="app")
    op.drop_constraint(
        "watch_event_origin_playback_event_id_fkey",
        "watch_event",
        schema="app",
        type_="foreignkey",
    )
    op.drop_column("watch_event", "origin_playback_event_id", schema="app")
    op.drop_column("watch_event", "origin_kind", schema="app")
