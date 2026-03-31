"""Add watch-event correction metadata and soft delete support."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

APP_SCHEMA = "app"

# revision identifiers, used by Alembic.
revision = "0010_add_watch_event_correction_fields"
down_revision = "0009_add_media_item_enrichment_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("watch_event", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True), schema=APP_SCHEMA)
    op.add_column("watch_event", sa.Column("updated_by", sa.String(), nullable=True), schema=APP_SCHEMA)
    op.add_column("watch_event", sa.Column("update_reason", sa.String(), nullable=True), schema=APP_SCHEMA)
    op.add_column(
        "watch_event",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema=APP_SCHEMA,
    )
    op.add_column("watch_event", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), schema=APP_SCHEMA)
    op.add_column("watch_event", sa.Column("deleted_by", sa.String(), nullable=True), schema=APP_SCHEMA)
    op.add_column("watch_event", sa.Column("deleted_reason", sa.String(), nullable=True), schema=APP_SCHEMA)
    op.create_index("ix_watch_event_is_deleted", "watch_event", ["is_deleted"], unique=False, schema=APP_SCHEMA)

    op.execute(
        """
        CREATE OR REPLACE VIEW app.v_show_progress AS
        WITH per_show AS (
            SELECT
                mi.show_id,
                mi.show_tmdb_id,
                s.title AS show_title,
                we.user_id,
                COUNT(*) FILTER (WHERE mi.type = 'episode'::public.media_type) AS total_episodes,
                COUNT(*) FILTER (
                    WHERE mi.type = 'episode'::public.media_type
                      AND we.completed = TRUE
                      AND COALESCE(we.is_deleted, FALSE) = FALSE
                ) AS watched_episodes
            FROM app.media_item AS mi
            JOIN app.shows AS s ON s.show_id = mi.show_id
            LEFT JOIN app.watch_event AS we
              ON we.media_item_id = mi.media_item_id
             AND COALESCE(we.is_deleted, FALSE) = FALSE
            WHERE mi.type = 'episode'::public.media_type
            GROUP BY mi.show_id, mi.show_tmdb_id, s.title, we.user_id
        )
        SELECT
            show_id,
            show_tmdb_id,
            show_title,
            user_id,
            total_episodes,
            watched_episodes,
            CASE
                WHEN total_episodes = 0 THEN 0::numeric(5,2)
                ELSE round((watched_episodes::numeric / total_episodes::numeric) * 100.0, 2)
            END AS watched_percent
        FROM per_show;
        """
    )

    op.execute("DROP TRIGGER IF EXISTS trg_watch_event_set_dedupe_hash ON app.watch_event")
    op.execute(
        """
        CREATE TRIGGER trg_watch_event_set_dedupe_hash
        BEFORE INSERT OR UPDATE ON app.watch_event
        FOR EACH ROW EXECUTE FUNCTION app.set_watch_event_dedupe_hash();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_watch_event_set_dedupe_hash ON app.watch_event")
    op.execute(
        """
        CREATE TRIGGER trg_watch_event_set_dedupe_hash
        BEFORE INSERT ON app.watch_event
        FOR EACH ROW EXECUTE FUNCTION app.set_watch_event_dedupe_hash();
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW app.v_show_progress AS
        WITH per_show AS (
            SELECT
                mi.show_id,
                mi.show_tmdb_id,
                s.title AS show_title,
                we.user_id,
                COUNT(*) FILTER (WHERE mi.type = 'episode'::public.media_type) AS total_episodes,
                COUNT(*) FILTER (
                    WHERE mi.type = 'episode'::public.media_type
                      AND we.completed = TRUE
                ) AS watched_episodes
            FROM app.media_item AS mi
            JOIN app.shows AS s ON s.show_id = mi.show_id
            LEFT JOIN app.watch_event AS we
              ON we.media_item_id = mi.media_item_id
            WHERE mi.type = 'episode'::public.media_type
            GROUP BY mi.show_id, mi.show_tmdb_id, s.title, we.user_id
        )
        SELECT
            show_id,
            show_tmdb_id,
            show_title,
            user_id,
            total_episodes,
            watched_episodes,
            CASE
                WHEN total_episodes = 0 THEN 0::numeric(5,2)
                ELSE round((watched_episodes::numeric / total_episodes::numeric) * 100.0, 2)
            END AS watched_percent
        FROM per_show;
        """
    )
    op.drop_index("ix_watch_event_is_deleted", table_name="watch_event", schema=APP_SCHEMA)
    op.drop_column("watch_event", "deleted_reason", schema=APP_SCHEMA)
    op.drop_column("watch_event", "deleted_by", schema=APP_SCHEMA)
    op.drop_column("watch_event", "deleted_at", schema=APP_SCHEMA)
    op.drop_column("watch_event", "is_deleted", schema=APP_SCHEMA)
    op.drop_column("watch_event", "update_reason", schema=APP_SCHEMA)
    op.drop_column("watch_event", "updated_by", schema=APP_SCHEMA)
    op.drop_column("watch_event", "updated_at", schema=APP_SCHEMA)
