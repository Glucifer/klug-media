"""Align show progress view with current schema backup."""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "0004_align_show_progress_view_with_backup"
down_revision = "0003_add_shows_and_progress_view"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE VIEW app.v_show_progress AS
        WITH totals AS (
            SELECT
                mi.show_id,
                COUNT(*) AS total_episodes
            FROM app.media_item AS mi
            WHERE mi.type = 'episode'::public.media_type
              AND mi.show_id IS NOT NULL
            GROUP BY mi.show_id
        ),
        watched AS (
            SELECT
                we.user_id,
                mi.show_id,
                COUNT(DISTINCT we.media_item_id) AS watched_episodes
            FROM app.watch_event AS we
            JOIN app.media_item AS mi
              ON mi.media_item_id = we.media_item_id
            WHERE mi.type = 'episode'::public.media_type
              AND mi.show_id IS NOT NULL
              AND we.completed = TRUE
            GROUP BY we.user_id, mi.show_id
        )
        SELECT
            s.show_id,
            s.tmdb_id AS show_tmdb_id,
            s.title AS show_title,
            w.user_id,
            t.total_episodes,
            w.watched_episodes,
            CASE
                WHEN t.total_episodes = 0 THEN 0::numeric
                ELSE ROUND(
                    (w.watched_episodes::numeric / t.total_episodes::numeric) * 100::numeric,
                    2
                )
            END AS watched_percent
        FROM watched AS w
        JOIN totals AS t
          ON t.show_id = w.show_id
        JOIN app.shows AS s
          ON s.show_id = w.show_id
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE VIEW app.v_show_progress AS
        WITH episode_items AS (
            SELECT
                mi.show_id,
                mi.media_item_id
            FROM app.media_item AS mi
            WHERE mi.type = 'episode'::public.media_type
              AND mi.show_id IS NOT NULL
        ),
        episode_counts AS (
            SELECT
                ei.show_id,
                COUNT(*) AS total_episodes
            FROM episode_items AS ei
            GROUP BY ei.show_id
        ),
        watched_counts AS (
            SELECT
                we.user_id,
                ei.show_id,
                COUNT(DISTINCT ei.media_item_id) AS watched_episodes
            FROM app.watch_event AS we
            JOIN episode_items AS ei
              ON ei.media_item_id = we.media_item_id
            WHERE we.completed = TRUE
            GROUP BY we.user_id, ei.show_id
        )
        SELECT
            s.show_id,
            s.tmdb_id AS show_tmdb_id,
            s.title AS show_title,
            u.user_id,
            ec.total_episodes,
            COALESCE(wc.watched_episodes, 0) AS watched_episodes,
            CASE
                WHEN ec.total_episodes = 0 THEN 0::numeric
                ELSE ROUND(
                    (COALESCE(wc.watched_episodes, 0)::numeric / ec.total_episodes::numeric) * 100::numeric,
                    2
                )
            END AS watched_percent
        FROM app.shows AS s
        JOIN episode_counts AS ec
          ON ec.show_id = s.show_id
        CROSS JOIN app.users AS u
        LEFT JOIN watched_counts AS wc
          ON wc.show_id = s.show_id
         AND wc.user_id = u.user_id
        """
    )
