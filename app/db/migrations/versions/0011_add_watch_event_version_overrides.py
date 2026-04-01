"""Add per-watch version and runtime overrides."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

APP_SCHEMA = "app"

# revision identifiers, used by Alembic.
revision = "0011_add_watch_event_version_overrides"
down_revision = "0010_add_watch_event_correction_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("watch_event", sa.Column("watch_version_name", sa.String(), nullable=True), schema=APP_SCHEMA)
    op.add_column("watch_event", sa.Column("watch_runtime_seconds", sa.Integer(), nullable=True), schema=APP_SCHEMA)

    op.execute(
        """
        CREATE OR REPLACE VIEW app.watch_event_enriched AS
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


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE VIEW app.watch_event_enriched AS
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
               COALESCE(v.version_key, 'default'::public.citext) AS version_key,
               COALESCE(v.version_name, 'Default/Theatrical') AS version_name,
               COALESCE(v.runtime_seconds, w.total_seconds, m.base_runtime_seconds) AS effective_runtime_seconds,
               CASE
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
               (COALESCE(v.runtime_seconds, w.total_seconds, m.base_runtime_seconds)::numeric / 3600.0) AS effective_runtime_hours,
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
    op.drop_column("watch_event", "watch_runtime_seconds", schema=APP_SCHEMA)
    op.drop_column("watch_event", "watch_version_name", schema=APP_SCHEMA)
