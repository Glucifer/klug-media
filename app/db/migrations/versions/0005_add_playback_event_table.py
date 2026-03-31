"""Add playback event persistence for scrobbler ingestion."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0005_add_playback_event_table"
down_revision = "0004_align_show_progress_view_with_backup"
branch_labels = None
depends_on = None

media_type_enum = postgresql.ENUM(
    "movie",
    "show",
    "episode",
    name="media_type",
    schema="public",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "playback_event",
        sa.Column(
            "playback_event_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("collector", sa.String(), nullable=False),
        sa.Column("playback_source", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_event_id", sa.String(), nullable=True),
        sa.Column("session_key", sa.String(), nullable=True),
        sa.Column(
            "media_type",
            media_type_enum,
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("season_number", sa.Integer(), nullable=True),
        sa.Column("episode_number", sa.Integer(), nullable=True),
        sa.Column("tmdb_id", sa.Integer(), nullable=True),
        sa.Column("imdb_id", sa.String(), nullable=True),
        sa.Column("tvdb_id", sa.Integer(), nullable=True),
        sa.Column("progress_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["app.users.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("playback_event_id"),
        schema="app",
    )
    op.create_index(
        "ix_playback_event_source_time",
        "playback_event",
        ["playback_source", sa.text("occurred_at DESC")],
        unique=False,
        schema="app",
    )
    op.create_index(
        "ix_playback_event_user_time",
        "playback_event",
        ["user_id", sa.text("occurred_at DESC")],
        unique=False,
        schema="app",
    )
    op.create_index(
        "ux_playback_event_source_event",
        "playback_event",
        ["collector", "source_event_id"],
        unique=True,
        schema="app",
        postgresql_where=sa.text("source_event_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ux_playback_event_source_event",
        table_name="playback_event",
        schema="app",
    )
    op.drop_index("ix_playback_event_user_time", table_name="playback_event", schema="app")
    op.drop_index(
        "ix_playback_event_source_time",
        table_name="playback_event",
        schema="app",
    )
    op.drop_table("playback_event", schema="app")
