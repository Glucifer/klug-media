"""Add media item enrichment fields."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0009_add_media_item_enrichment_fields"
down_revision = "0008_add_watch_event_origin_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("media_item", sa.Column("summary", sa.Text(), nullable=True), schema="app")
    op.add_column("media_item", sa.Column("poster_url", sa.Text(), nullable=True), schema="app")
    op.add_column("media_item", sa.Column("release_date", sa.Date(), nullable=True), schema="app")
    op.add_column(
        "media_item",
        sa.Column(
            "enrichment_status",
            sa.String(),
            nullable=False,
            server_default=sa.text("'pending'::text"),
        ),
        schema="app",
    )
    op.add_column(
        "media_item",
        sa.Column("enrichment_error", sa.Text(), nullable=True),
        schema="app",
    )
    op.add_column(
        "media_item",
        sa.Column("enrichment_attempted_at", sa.DateTime(timezone=True), nullable=True),
        schema="app",
    )
    op.create_index(
        "ix_media_item_enrichment_status",
        "media_item",
        ["enrichment_status"],
        unique=False,
        schema="app",
    )

    op.execute(
        """
        UPDATE app.media_item AS mi
        SET
            enrichment_status = CASE
                WHEN mi.type = 'movie'::public.media_type
                    AND (mi.tmdb_id IS NOT NULL OR mi.imdb_id IS NOT NULL)
                    THEN 'pending'
                WHEN mi.type = 'show'::public.media_type
                    AND (mi.tmdb_id IS NOT NULL OR mi.tvdb_id IS NOT NULL OR mi.imdb_id IS NOT NULL)
                    THEN 'pending'
                WHEN mi.type = 'episode'::public.media_type
                    AND (mi.show_tmdb_id IS NOT NULL OR mi.tvdb_id IS NOT NULL OR mi.tmdb_id IS NOT NULL)
                    THEN 'pending'
                ELSE 'skipped'
            END,
            enrichment_error = CASE
                WHEN mi.type = 'movie'::public.media_type
                    AND (mi.tmdb_id IS NOT NULL OR mi.imdb_id IS NOT NULL)
                    THEN NULL
                WHEN mi.type = 'show'::public.media_type
                    AND (mi.tmdb_id IS NOT NULL OR mi.tvdb_id IS NOT NULL OR mi.imdb_id IS NOT NULL)
                    THEN NULL
                WHEN mi.type = 'episode'::public.media_type
                    AND (mi.show_tmdb_id IS NOT NULL OR mi.tvdb_id IS NOT NULL OR mi.tmdb_id IS NOT NULL)
                    THEN NULL
                ELSE 'missing_supported_external_id'
            END
        """
    )


def downgrade() -> None:
    op.drop_index("ix_media_item_enrichment_status", table_name="media_item", schema="app")
    op.drop_column("media_item", "enrichment_attempted_at", schema="app")
    op.drop_column("media_item", "enrichment_error", schema="app")
    op.drop_column("media_item", "enrichment_status", schema="app")
    op.drop_column("media_item", "release_date", schema="app")
    op.drop_column("media_item", "poster_url", schema="app")
    op.drop_column("media_item", "summary", schema="app")
