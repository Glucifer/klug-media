"""Initial Klug Media schema baseline."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

APP_SCHEMA = "app"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public")
    op.execute("CREATE SCHEMA IF NOT EXISTS app")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'media_type' AND n.nspname = 'public'
            ) THEN
                CREATE TYPE public.media_type AS ENUM ('movie', 'show', 'episode');
            END IF;
        END$$;
        """
    )

    media_type = postgresql.ENUM("movie", "show", "episode", name="media_type", schema="public", create_type=False)

    op.create_table(
        "import_batch",
        sa.Column(
            "import_batch_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_detail", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Text(), server_default=sa.text("'running'::text"), nullable=False),
        sa.Column("watch_events_inserted", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("media_items_inserted", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("media_versions_inserted", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("tags_added", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("errors_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("import_batch_id", name="import_batch_pkey"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "media_item",
        sa.Column(
            "media_item_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("type", media_type, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("tmdb_id", sa.Integer(), nullable=True),
        sa.Column("imdb_id", sa.Text(), nullable=True),
        sa.Column("tvdb_id", sa.Integer(), nullable=True),
        sa.Column("show_tmdb_id", sa.Integer(), nullable=True),
        sa.Column("season_number", sa.Integer(), nullable=True),
        sa.Column("episode_number", sa.Integer(), nullable=True),
        sa.Column("jellyfin_item_id", sa.Text(), nullable=True),
        sa.Column("kodi_item_id", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("base_runtime_seconds", sa.Integer(), nullable=True),
        sa.Column("metadata_source", sa.Text(), nullable=True),
        sa.Column("metadata_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("media_item_id", name="media_item_pkey"),
        sa.UniqueConstraint("type", "imdb_id", name="uq_media_imdb"),
        sa.UniqueConstraint("type", "tmdb_id", name="uq_media_tmdb"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "media_version",
        sa.Column(
            "media_version_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("media_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_key", postgresql.CITEXT(), nullable=False),
        sa.Column("version_name", sa.Text(), nullable=False),
        sa.Column("runtime_seconds", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["media_item_id"],
            [f"{APP_SCHEMA}.media_item.media_item_id"],
            name="media_version_media_item_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("media_version_id", name="media_version_pkey"),
        sa.UniqueConstraint("media_item_id", "media_version_id", name="media_version_item_version_uk"),
        sa.UniqueConstraint("media_item_id", "version_key", name="uq_media_version"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "tag",
        sa.Column(
            "tag_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tag_key", postgresql.CITEXT(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "horrorfest_year",
            sa.Integer(),
            sa.Computed(
                "CASE "
                "WHEN (tag_key::text ~* '^horrorfest_[0-9]{4}$') "
                "THEN right(tag_key::text, 4)::integer "
                "ELSE NULL::integer END",
                persisted=True,
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("tag_id", name="tag_pkey"),
        sa.UniqueConstraint("tag_key", name="tag_tag_key_key"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "tmdb_metadata_cache",
        sa.Column("tmdb_type", sa.Text(), nullable=False),
        sa.Column("tmdb_id", sa.Integer(), nullable=False),
        sa.Column("sub_key", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("etag", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("tmdb_type", "tmdb_id", "sub_key", name="tmdb_metadata_cache_pkey"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("username", postgresql.CITEXT(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("user_id", name="users_pkey"),
        sa.UniqueConstraint("username", name="users_username_key"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "import_batch_error",
        sa.Column(
            "import_batch_error_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("severity", sa.Text(), server_default=sa.text("'error'::text"), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=True),
        sa.Column("entity_ref", sa.Text(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.ForeignKeyConstraint(
            ["import_batch_id"],
            [f"{APP_SCHEMA}.import_batch.import_batch_id"],
            name="import_batch_error_import_batch_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("import_batch_error_id", name="import_batch_error_pkey"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "watch_event",
        sa.Column("watch_id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("media_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("watched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("playback_source", sa.Text(), nullable=False),
        sa.Column("total_seconds", sa.Integer(), nullable=True),
        sa.Column("watched_seconds", sa.Integer(), nullable=True),
        sa.Column("progress_percent", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("completed", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("rating_value", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("rating_scale", sa.Text(), nullable=True),
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("rewatch", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("media_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("dedupe_hash", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.Column("source_event_id", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["import_batch_id"],
            [f"{APP_SCHEMA}.import_batch.import_batch_id"],
            name="fk_watch_event_import_batch",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["media_item_id"],
            [f"{APP_SCHEMA}.media_item.media_item_id"],
            name="watch_event_media_item_id_fkey",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["media_version_id"],
            [f"{APP_SCHEMA}.media_version.media_version_id"],
            name="watch_event_media_version_id_fkey",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            [f"{APP_SCHEMA}.users.user_id"],
            name="watch_event_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["media_item_id", "media_version_id"],
            [f"{APP_SCHEMA}.media_version.media_item_id", f"{APP_SCHEMA}.media_version.media_version_id"],
            name="watch_event_version_matches_item",
            deferrable=True,
            initially="DEFERRED",
        ),
        sa.PrimaryKeyConstraint("watch_id", name="watch_event_pkey"),
        schema=APP_SCHEMA,
    )

    op.create_table(
        "watch_event_tag",
        sa.Column("watch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            [f"{APP_SCHEMA}.tag.tag_id"],
            name="watch_event_tag_tag_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["watch_id"],
            [f"{APP_SCHEMA}.watch_event.watch_id"],
            name="watch_event_tag_watch_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("watch_id", "tag_id", name="watch_event_tag_pkey"),
        schema=APP_SCHEMA,
    )

    op.create_index("ix_import_batch_started_at", "import_batch", [sa.text("started_at DESC")], schema=APP_SCHEMA)
    op.create_index("ix_import_batch_status", "import_batch", ["status"], schema=APP_SCHEMA)
    op.create_index("ix_import_batch_error_batch", "import_batch_error", ["import_batch_id"], schema=APP_SCHEMA)
    op.create_index(
        "ix_import_batch_error_time",
        "import_batch_error",
        [sa.text("occurred_at DESC")],
        schema=APP_SCHEMA,
    )
    op.create_index("ix_media_item_tmdb", "media_item", ["tmdb_id"], schema=APP_SCHEMA)
    op.create_index("ix_media_version_item", "media_version", ["media_item_id"], schema=APP_SCHEMA)
    op.create_index("ix_tmdb_cache_expires_at", "tmdb_metadata_cache", ["expires_at"], schema=APP_SCHEMA)
    op.create_index("ix_tmdb_cache_fetched_at", "tmdb_metadata_cache", [sa.text("fetched_at DESC")], schema=APP_SCHEMA)
    op.create_index(
        "ix_watch_event_source_event",
        "watch_event",
        ["playback_source", "source_event_id"],
        unique=False,
        schema=APP_SCHEMA,
        postgresql_where=sa.text("source_event_id IS NOT NULL"),
    )
    op.create_index("ix_watch_event_user_time", "watch_event", ["user_id", sa.text("watched_at DESC")], schema=APP_SCHEMA)
    op.create_index("ix_watch_event_watched_at", "watch_event", [sa.text("watched_at DESC")], schema=APP_SCHEMA)
    op.create_index(
        "ux_watch_event_dedupe_hash",
        "watch_event",
        ["dedupe_hash"],
        unique=True,
        schema=APP_SCHEMA,
        postgresql_where=sa.text("dedupe_hash IS NOT NULL"),
    )

    op.execute(
        """
        CREATE FUNCTION app.create_default_media_version() RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          INSERT INTO app.media_version (
            media_item_id,
            version_key,
            version_name
          )
          VALUES (
            NEW.media_item_id,
            'default',
            'Default/Theatrical'
          )
          ON CONFLICT (media_item_id, version_key) DO NOTHING;

          RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE FUNCTION app.set_watch_event_dedupe_hash() RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
          v_bucket timestamptz;
          v_payload text;
        BEGIN
          IF NEW.dedupe_hash IS NULL OR NEW.dedupe_hash = '' THEN
            v_bucket := date_trunc('minute', NEW.watched_at);

            v_payload :=
              NEW.user_id::text || '|' ||
              NEW.media_item_id::text || '|' ||
              NEW.playback_source || '|' ||
              v_bucket::text || '|' ||
              COALESCE(NEW.media_version_id::text, '') || '|' ||
              COALESCE(NEW.completed::text, '') || '|' ||
              COALESCE(NEW.progress_percent::text, '') || '|' ||
              COALESCE(NEW.total_seconds::text, '') || '|' ||
              COALESCE(NEW.watched_seconds::text, '');

            NEW.dedupe_hash := encode(digest(v_payload, 'sha256'), 'hex');
          END IF;

          RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE VIEW app.tmdb_movie_basic AS
        SELECT tmdb_id,
               (payload ->> 'title') AS title,
               ((payload ->> 'runtime'))::integer AS runtime_minutes,
               fetched_at
        FROM app.tmdb_metadata_cache
        WHERE (tmdb_type = 'movie' AND sub_key IS NULL);
        """
    )

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

    op.execute(
        """
        CREATE TRIGGER trg_create_default_media_version
        AFTER INSERT ON app.media_item
        FOR EACH ROW EXECUTE FUNCTION app.create_default_media_version();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_watch_event_set_dedupe_hash
        BEFORE INSERT ON app.watch_event
        FOR EACH ROW EXECUTE FUNCTION app.set_watch_event_dedupe_hash();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_watch_event_set_dedupe_hash ON app.watch_event")
    op.execute("DROP TRIGGER IF EXISTS trg_create_default_media_version ON app.media_item")
    op.execute("DROP VIEW IF EXISTS app.watch_event_enriched")
    op.execute("DROP VIEW IF EXISTS app.tmdb_movie_basic")
    op.execute("DROP FUNCTION IF EXISTS app.set_watch_event_dedupe_hash()")
    op.execute("DROP FUNCTION IF EXISTS app.create_default_media_version()")

    op.drop_index("ux_watch_event_dedupe_hash", table_name="watch_event", schema=APP_SCHEMA)
    op.drop_index("ix_watch_event_watched_at", table_name="watch_event", schema=APP_SCHEMA)
    op.drop_index("ix_watch_event_user_time", table_name="watch_event", schema=APP_SCHEMA)
    op.drop_index("ix_watch_event_source_event", table_name="watch_event", schema=APP_SCHEMA)
    op.drop_index("ix_tmdb_cache_fetched_at", table_name="tmdb_metadata_cache", schema=APP_SCHEMA)
    op.drop_index("ix_tmdb_cache_expires_at", table_name="tmdb_metadata_cache", schema=APP_SCHEMA)
    op.drop_index("ix_media_version_item", table_name="media_version", schema=APP_SCHEMA)
    op.drop_index("ix_media_item_tmdb", table_name="media_item", schema=APP_SCHEMA)
    op.drop_index("ix_import_batch_error_time", table_name="import_batch_error", schema=APP_SCHEMA)
    op.drop_index("ix_import_batch_error_batch", table_name="import_batch_error", schema=APP_SCHEMA)
    op.drop_index("ix_import_batch_status", table_name="import_batch", schema=APP_SCHEMA)
    op.drop_index("ix_import_batch_started_at", table_name="import_batch", schema=APP_SCHEMA)

    op.drop_table("watch_event_tag", schema=APP_SCHEMA)
    op.drop_table("watch_event", schema=APP_SCHEMA)
    op.drop_table("import_batch_error", schema=APP_SCHEMA)
    op.drop_table("users", schema=APP_SCHEMA)
    op.drop_table("tmdb_metadata_cache", schema=APP_SCHEMA)
    op.drop_table("tag", schema=APP_SCHEMA)
    op.drop_table("media_version", schema=APP_SCHEMA)
    op.drop_table("media_item", schema=APP_SCHEMA)
    op.drop_table("import_batch", schema=APP_SCHEMA)

    op.execute("DROP TYPE IF EXISTS public.media_type")
    op.execute("DROP SCHEMA IF EXISTS app")
