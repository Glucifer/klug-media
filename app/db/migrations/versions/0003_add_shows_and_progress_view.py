"""Add shows table and show progress view."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0003_add_shows_and_progress_view"
down_revision = "0002_watch_event_source_event_unique"
branch_labels = None
depends_on = None

APP_SCHEMA = "app"


def upgrade() -> None:
    op.create_table(
        "shows",
        sa.Column(
            "show_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tmdb_id", sa.Integer(), nullable=False),
        sa.Column("tvdb_id", sa.Integer(), nullable=True),
        sa.Column("imdb_id", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("show_id", name="shows_pkey"),
        sa.UniqueConstraint("tmdb_id", name="uq_shows_tmdb"),
        schema=APP_SCHEMA,
    )
    op.create_index("ix_shows_imdb_id", "shows", ["imdb_id"], schema=APP_SCHEMA)
    op.create_index("ix_shows_tvdb_id", "shows", ["tvdb_id"], schema=APP_SCHEMA)

    op.add_column(
        "media_item",
        sa.Column("show_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema=APP_SCHEMA,
    )
    op.create_index("ix_media_item_show_id", "media_item", ["show_id"], schema=APP_SCHEMA)
    op.create_index(
        "ix_media_item_show_tmdb", "media_item", ["show_tmdb_id"], schema=APP_SCHEMA
    )
    op.create_index(
        "ux_media_item_episode_key",
        "media_item",
        ["show_tmdb_id", "season_number", "episode_number"],
        unique=True,
        schema=APP_SCHEMA,
        postgresql_where=sa.text(
            "type = 'episode'::public.media_type AND show_tmdb_id IS NOT NULL"
        ),
    )
    op.create_foreign_key(
        "fk_media_item_show",
        source_table="media_item",
        referent_table="shows",
        local_cols=["show_id"],
        remote_cols=["show_id"],
        source_schema=APP_SCHEMA,
        referent_schema=APP_SCHEMA,
        ondelete="SET NULL",
    )

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


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS app.v_show_progress")
    op.drop_constraint(
        "fk_media_item_show",
        "media_item",
        schema=APP_SCHEMA,
        type_="foreignkey",
    )
    op.drop_index(
        "ux_media_item_episode_key",
        table_name="media_item",
        schema=APP_SCHEMA,
    )
    op.drop_index("ix_media_item_show_tmdb", table_name="media_item", schema=APP_SCHEMA)
    op.drop_index("ix_media_item_show_id", table_name="media_item", schema=APP_SCHEMA)
    op.drop_column("media_item", "show_id", schema=APP_SCHEMA)

    op.drop_index("ix_shows_tvdb_id", table_name="shows", schema=APP_SCHEMA)
    op.drop_index("ix_shows_imdb_id", table_name="shows", schema=APP_SCHEMA)
    op.drop_table("shows", schema=APP_SCHEMA)
