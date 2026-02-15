from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Computed,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import UniqueConstraint, text
from sqlalchemy.dialects.postgresql import CITEXT, ENUM, JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

APP_SCHEMA = "app"
MEDIA_TYPE_ENUM = ENUM(
    "movie",
    "show",
    "episode",
    name="media_type",
    schema="public",
    create_type=False,
)


class ImportBatch(Base):
    __tablename__ = "import_batch"
    __table_args__ = (
        Index("ix_import_batch_started_at", text("started_at DESC")),
        Index("ix_import_batch_status", "status"),
        {"schema": APP_SCHEMA},
    )

    import_batch_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    source: Mapped[str] = mapped_column(String, nullable=False)
    source_detail: Mapped[str | None] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        String, server_default=text("'running'::text"), nullable=False
    )
    watch_events_inserted: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    media_items_inserted: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    media_versions_inserted: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    tags_added: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    errors_count: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    parameters: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(String)

    import_errors: Mapped[list[ImportBatchError]] = relationship(
        back_populates="import_batch"
    )
    watch_events: Mapped[list[WatchEvent]] = relationship(back_populates="import_batch")


class ImportBatchError(Base):
    __tablename__ = "import_batch_error"
    __table_args__ = (
        Index("ix_import_batch_error_batch", "import_batch_id"),
        Index("ix_import_batch_error_time", text("occurred_at DESC")),
        {"schema": APP_SCHEMA},
    )

    import_batch_error_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    import_batch_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(f"{APP_SCHEMA}.import_batch.import_batch_id", ondelete="CASCADE"),
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    severity: Mapped[str] = mapped_column(
        String, server_default=text("'error'::text"), nullable=False
    )
    entity_type: Mapped[str | None] = mapped_column(String)
    entity_ref: Mapped[str | None] = mapped_column(String)
    message: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb"), nullable=False
    )

    import_batch: Mapped[ImportBatch] = relationship(back_populates="import_errors")


class MediaItem(Base):
    __tablename__ = "media_item"
    __table_args__ = (
        UniqueConstraint("type", "imdb_id", name="uq_media_imdb"),
        UniqueConstraint("type", "tmdb_id", name="uq_media_tmdb"),
        Index("ix_media_item_tmdb", "tmdb_id"),
        {"schema": APP_SCHEMA},
    )

    media_item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    type: Mapped[str] = mapped_column(MEDIA_TYPE_ENUM, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)
    tmdb_id: Mapped[int | None] = mapped_column(Integer)
    imdb_id: Mapped[str | None] = mapped_column(String)
    tvdb_id: Mapped[int | None] = mapped_column(Integer)
    show_tmdb_id: Mapped[int | None] = mapped_column(Integer)
    season_number: Mapped[int | None] = mapped_column(Integer)
    episode_number: Mapped[int | None] = mapped_column(Integer)
    jellyfin_item_id: Mapped[str | None] = mapped_column(String)
    kodi_item_id: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    base_runtime_seconds: Mapped[int | None] = mapped_column(Integer)
    metadata_source: Mapped[str | None] = mapped_column(String)
    metadata_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    media_versions: Mapped[list[MediaVersion]] = relationship(
        back_populates="media_item"
    )
    watch_events: Mapped[list[WatchEvent]] = relationship(back_populates="media_item")


class MediaVersion(Base):
    __tablename__ = "media_version"
    __table_args__ = (
        UniqueConstraint(
            "media_item_id", "media_version_id", name="media_version_item_version_uk"
        ),
        UniqueConstraint("media_item_id", "version_key", name="uq_media_version"),
        Index("ix_media_version_item", "media_item_id"),
        {"schema": APP_SCHEMA},
    )

    media_version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    media_item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(f"{APP_SCHEMA}.media_item.media_item_id", ondelete="CASCADE"),
        nullable=False,
    )
    version_key: Mapped[str] = mapped_column(CITEXT, nullable=False)
    version_name: Mapped[str] = mapped_column(String, nullable=False)
    runtime_seconds: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    media_item: Mapped[MediaItem] = relationship(back_populates="media_versions")
    watch_events: Mapped[list[WatchEvent]] = relationship(
        back_populates="media_version",
        foreign_keys="WatchEvent.media_version_id",
    )


class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = {"schema": APP_SCHEMA}

    tag_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tag_key: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    horrorfest_year: Mapped[int | None] = mapped_column(
        Integer,
        Computed(
            "CASE "
            "WHEN (tag_key::text ~* '^horrorfest_[0-9]{4}$') "
            "THEN right(tag_key::text, 4)::integer "
            "ELSE NULL::integer END",
            persisted=True,
        ),
    )

    watch_event_tags: Mapped[list[WatchEventTag]] = relationship(back_populates="tag")


class TmdbMetadataCache(Base):
    __tablename__ = "tmdb_metadata_cache"
    __table_args__ = (
        Index("ix_tmdb_cache_expires_at", "expires_at"),
        Index("ix_tmdb_cache_fetched_at", text("fetched_at DESC")),
        {"schema": APP_SCHEMA},
    )

    tmdb_type: Mapped[str] = mapped_column(String, primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sub_key: Mapped[str] = mapped_column(String, primary_key=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    etag: Mapped[str | None] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(String)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": APP_SCHEMA}

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    username: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    watch_events: Mapped[list[WatchEvent]] = relationship(back_populates="user")


class WatchEvent(Base):
    __tablename__ = "watch_event"
    __table_args__ = (
        ForeignKeyConstraint(
            ["media_item_id", "media_version_id"],
            [
                f"{APP_SCHEMA}.media_version.media_item_id",
                f"{APP_SCHEMA}.media_version.media_version_id",
            ],
            name="watch_event_version_matches_item",
            deferrable=True,
            initially="DEFERRED",
        ),
        Index(
            "ix_watch_event_source_event",
            "playback_source",
            "source_event_id",
            postgresql_where=text("source_event_id IS NOT NULL"),
        ),
        Index("ix_watch_event_user_time", "user_id", text("watched_at DESC")),
        Index("ix_watch_event_watched_at", text("watched_at DESC")),
        Index(
            "ux_watch_event_dedupe_hash",
            "dedupe_hash",
            unique=True,
            postgresql_where=text("dedupe_hash IS NOT NULL"),
        ),
        {"schema": APP_SCHEMA},
    )

    watch_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(f"{APP_SCHEMA}.users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    media_item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(f"{APP_SCHEMA}.media_item.media_item_id", ondelete="RESTRICT"),
        nullable=False,
    )
    watched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    playback_source: Mapped[str] = mapped_column(String, nullable=False)
    total_seconds: Mapped[int | None] = mapped_column(Integer)
    watched_seconds: Mapped[int | None] = mapped_column(Integer)
    progress_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    completed: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), nullable=False
    )
    rating_value: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    rating_scale: Mapped[str | None] = mapped_column(String)
    import_batch_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(f"{APP_SCHEMA}.import_batch.import_batch_id", ondelete="SET NULL"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    rewatch: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    media_version_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(f"{APP_SCHEMA}.media_version.media_version_id", ondelete="SET NULL"),
    )
    dedupe_hash: Mapped[str | None] = mapped_column(String)
    created_by: Mapped[str | None] = mapped_column(String)
    source_event_id: Mapped[str | None] = mapped_column(String)

    user: Mapped[User] = relationship(back_populates="watch_events")
    media_item: Mapped[MediaItem] = relationship(back_populates="watch_events")
    media_version: Mapped[MediaVersion | None] = relationship(
        back_populates="watch_events",
        foreign_keys=[media_version_id],
    )
    import_batch: Mapped[ImportBatch | None] = relationship(
        back_populates="watch_events"
    )
    watch_event_tags: Mapped[list[WatchEventTag]] = relationship(
        back_populates="watch_event"
    )


class WatchEventTag(Base):
    __tablename__ = "watch_event_tag"
    __table_args__ = {"schema": APP_SCHEMA}

    watch_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(f"{APP_SCHEMA}.watch_event.watch_id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(f"{APP_SCHEMA}.tag.tag_id", ondelete="CASCADE"),
        primary_key=True,
    )

    watch_event: Mapped[WatchEvent] = relationship(back_populates="watch_event_tags")
    tag: Mapped[Tag] = relationship(back_populates="watch_event_tags")
