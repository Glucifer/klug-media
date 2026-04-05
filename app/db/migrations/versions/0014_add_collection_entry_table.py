"""Add owned-media collection entries and relax show TMDB requirement."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0014_add_collection_entry_table"
down_revision = "0013_filter_deleted_from_watch_event_enriched"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("shows", "tmdb_id", schema="app", existing_type=sa.Integer(), nullable=True)

    op.create_table(
        "collection_entry",
        sa.Column(
            "collection_entry_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("source_item_id", sa.String(), nullable=False),
        sa.Column(
            "item_type",
            postgresql.ENUM(
                "movie",
                "show",
                "episode",
                name="media_type",
                schema="public",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("media_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("show_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("library_id", sa.String(), nullable=False),
        sa.Column("library_name", sa.String(), nullable=True),
        sa.Column("is_present", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("missing_since", sa.DateTime(timezone=True), nullable=True),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("runtime_seconds", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column(
            "source_data",
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
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "("
            "(item_type = 'show'::public.media_type AND show_id IS NOT NULL AND media_item_id IS NULL) OR "
            "(item_type IN ('movie'::public.media_type, 'episode'::public.media_type) "
            "AND media_item_id IS NOT NULL AND show_id IS NULL)"
            ")",
            name="ck_collection_entry_item_target",
        ),
        sa.ForeignKeyConstraint(
            ["media_item_id"],
            ["app.media_item.media_item_id"],
            name="collection_entry_media_item_id_fkey",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["show_id"],
            ["app.shows.show_id"],
            name="collection_entry_show_id_fkey",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("collection_entry_id", name="collection_entry_pkey"),
        sa.UniqueConstraint("source", "source_item_id", name="uq_collection_entry_source_item"),
        schema="app",
    )
    op.create_index(
        "ix_collection_entry_present",
        "collection_entry",
        ["source", "is_present"],
        schema="app",
    )
    op.create_index(
        "ix_collection_entry_library",
        "collection_entry",
        ["source", "library_id"],
        schema="app",
    )


def downgrade() -> None:
    op.drop_index("ix_collection_entry_library", table_name="collection_entry", schema="app")
    op.drop_index("ix_collection_entry_present", table_name="collection_entry", schema="app")
    op.drop_table("collection_entry", schema="app")
    op.alter_column("shows", "tmdb_id", schema="app", existing_type=sa.Integer(), nullable=False)
