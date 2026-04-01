"""Add Horrorfest year and entry overlay tables."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

APP_SCHEMA = "app"

# revision identifiers, used by Alembic.
revision = "0012_add_horrorfest_overlay"
down_revision = "0011_add_watch_event_version_overrides"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "horrorfest_year",
        sa.Column("horrorfest_year", sa.Integer(), nullable=False),
        sa.Column("window_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("horrorfest_year", name="horrorfest_year_pkey"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "horrorfest_entry",
        sa.Column(
            "horrorfest_entry_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("watch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("horrorfest_year", sa.Integer(), nullable=False),
        sa.Column("watch_order", sa.Integer(), nullable=True),
        sa.Column("source_kind", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("update_reason", sa.String(), nullable=True),
        sa.Column(
            "is_removed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("removed_by", sa.String(), nullable=True),
        sa.Column("removed_reason", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["horrorfest_year"],
            [f"{APP_SCHEMA}.horrorfest_year.horrorfest_year"],
            name="horrorfest_entry_horrorfest_year_fkey",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["watch_id"],
            [f"{APP_SCHEMA}.watch_event.watch_id"],
            name="horrorfest_entry_watch_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("horrorfest_entry_id", name="horrorfest_entry_pkey"),
        schema=APP_SCHEMA,
    )

    op.create_index(
        "ix_horrorfest_entry_year_order",
        "horrorfest_entry",
        ["horrorfest_year", "watch_order"],
        schema=APP_SCHEMA,
    )
    op.create_index(
        "ux_horrorfest_entry_watch_active",
        "horrorfest_entry",
        ["watch_id"],
        unique=True,
        schema=APP_SCHEMA,
        postgresql_where=sa.text("is_removed IS FALSE"),
    )
    op.create_index(
        "ux_horrorfest_entry_year_order_active",
        "horrorfest_entry",
        ["horrorfest_year", "watch_order"],
        unique=True,
        schema=APP_SCHEMA,
        postgresql_where=sa.text("is_removed IS FALSE AND watch_order IS NOT NULL"),
    )

    op.execute("DROP VIEW IF EXISTS app.watch_event_enriched")
    op.execute(
        """
        CREATE VIEW app.watch_event_enriched AS
        WITH horrorfest_entries AS (
            SELECT he.watch_id,
                   he.horrorfest_year,
                   he.watch_order
            FROM app.horrorfest_entry he
            WHERE he.is_removed IS FALSE
        )
        SELECT w.watch_id,
               w.user_id,
               u.username,
               w.watched_at,
               (w.watched_at AT TIME ZONE 'America/Edmonton') AS watched_local_ts,
               ((w.watched_at AT TIME ZONE 'America/Edmonton'))::date AS watched_local_date,
               (EXTRACT(year FROM (w.watched_at AT TIME ZONE 'America/Edmonton')))::integer AS watched_local_year,
               (EXTRACT(month FROM (w.watched_at AT TIME ZONE 'America/Edmonton')))::integer AS watched_local_month,
               w.playback_source,
               w.completed,
               w.rewatch,
               m.media_item_id,
               m.type AS media_type,
               m.title,
               m.year,
               m.tmdb_id,
               m.imdb_id,
               m.tvdb_id,
               m.show_tmdb_id,
               m.season_number,
               m.episode_number,
               m.jellyfin_item_id,
               m.kodi_item_id,
               w.media_version_id,
               COALESCE(w.watch_version_name::citext, v.version_key, 'default'::public.citext) AS version_key,
               COALESCE(w.watch_version_name::text, v.version_name::text, 'Default/Theatrical'::text) AS version_name,
               COALESCE(w.watch_runtime_seconds, v.runtime_seconds, w.total_seconds, m.base_runtime_seconds) AS effective_runtime_seconds,
               CASE
                   WHEN w.watch_runtime_seconds IS NOT NULL THEN 'watch_override'
                   WHEN v.runtime_seconds IS NOT NULL THEN 'version_override'
                   WHEN w.total_seconds IS NOT NULL THEN 'player_total'
                   WHEN m.base_runtime_seconds IS NOT NULL THEN 'base_runtime'
                   ELSE 'unknown'
               END AS runtime_source,
               w.total_seconds,
               w.watched_seconds,
               w.progress_percent,
               w.rating_value,
               w.rating_scale,
               (COALESCE(w.watch_runtime_seconds, v.runtime_seconds, w.total_seconds, m.base_runtime_seconds)::numeric / 3600.0) AS effective_runtime_hours,
               he.horrorfest_year,
               w.import_batch_id,
               w.created_at,
               he.watch_order AS horrorfest_watch_order
        FROM app.watch_event w
        JOIN app.users u ON u.user_id = w.user_id
        JOIN app.media_item m ON m.media_item_id = w.media_item_id
        LEFT JOIN app.media_version v ON v.media_version_id = w.media_version_id
        LEFT JOIN horrorfest_entries he ON he.watch_id = w.watch_id;
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS app.watch_event_enriched")
    op.execute(
        """
        CREATE VIEW app.watch_event_enriched AS
        WITH horrorfest_tags AS (
            SELECT wet.watch_id,
                   min(t.horrorfest_year) AS horrorfest_year
            FROM app.watch_event_tag wet
            JOIN app.tag t ON t.tag_id = wet.tag_id
            WHERE t.horrorfest_year IS NOT NULL
            GROUP BY wet.watch_id
        )
        SELECT w.watch_id,
               w.user_id,
               u.username,
               w.watched_at,
               (w.watched_at AT TIME ZONE 'America/Edmonton') AS watched_local_ts,
               ((w.watched_at AT TIME ZONE 'America/Edmonton'))::date AS watched_local_date,
               (EXTRACT(year FROM (w.watched_at AT TIME ZONE 'America/Edmonton')))::integer AS watched_local_year,
               (EXTRACT(month FROM (w.watched_at AT TIME ZONE 'America/Edmonton')))::integer AS watched_local_month,
               w.playback_source,
               w.completed,
               w.rewatch,
               m.media_item_id,
               m.type AS media_type,
               m.title,
               m.year,
               m.tmdb_id,
               m.imdb_id,
               m.tvdb_id,
               m.show_tmdb_id,
               m.season_number,
               m.episode_number,
               m.jellyfin_item_id,
               m.kodi_item_id,
               w.media_version_id,
               COALESCE(w.watch_version_name::citext, v.version_key, 'default'::public.citext) AS version_key,
               COALESCE(w.watch_version_name::text, v.version_name::text, 'Default/Theatrical'::text) AS version_name,
               COALESCE(w.watch_runtime_seconds, v.runtime_seconds, w.total_seconds, m.base_runtime_seconds) AS effective_runtime_seconds,
               CASE
                   WHEN w.watch_runtime_seconds IS NOT NULL THEN 'watch_override'
                   WHEN v.runtime_seconds IS NOT NULL THEN 'version_override'
                   WHEN w.total_seconds IS NOT NULL THEN 'player_total'
                   WHEN m.base_runtime_seconds IS NOT NULL THEN 'base_runtime'
                   ELSE 'unknown'
               END AS runtime_source,
               w.total_seconds,
               w.watched_seconds,
               w.progress_percent,
               w.rating_value,
               w.rating_scale,
               (COALESCE(w.watch_runtime_seconds, v.runtime_seconds, w.total_seconds, m.base_runtime_seconds)::numeric / 3600.0) AS effective_runtime_hours,
               ht.horrorfest_year,
               w.import_batch_id,
               w.created_at
        FROM app.watch_event w
        JOIN app.users u ON u.user_id = w.user_id
        JOIN app.media_item m ON m.media_item_id = w.media_item_id
        LEFT JOIN app.media_version v ON v.media_version_id = w.media_version_id
        LEFT JOIN horrorfest_tags ht ON ht.watch_id = w.watch_id;
        """
    )

    op.drop_index(
        "ux_horrorfest_entry_year_order_active",
        table_name="horrorfest_entry",
        schema=APP_SCHEMA,
    )
    op.drop_index(
        "ux_horrorfest_entry_watch_active",
        table_name="horrorfest_entry",
        schema=APP_SCHEMA,
    )
    op.drop_index(
        "ix_horrorfest_entry_year_order",
        table_name="horrorfest_entry",
        schema=APP_SCHEMA,
    )
    op.drop_table("horrorfest_entry", schema=APP_SCHEMA)
    op.drop_table("horrorfest_year", schema=APP_SCHEMA)
