from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories import media_items as media_item_repository
from app.services.shows import ShowService


@dataclass(frozen=True)
class ShowBackfillResult:
    scanned_count: int
    linked_count: int
    shows_created_count: int
    dry_run: bool


class ShowBackfillService:
    @staticmethod
    def backfill_episode_show_links(
        session: Session,
        *,
        dry_run: bool,
        limit: int | None = None,
    ) -> ShowBackfillResult:
        episodes = media_item_repository.list_episode_media_items_missing_show_id(
            session,
            limit=limit,
        )

        linked_count = 0
        shows_created_count = 0
        planned_shows: set[int] = set()

        for episode in episodes:
            if episode.show_tmdb_id is None:
                continue

            existing_show = ShowService.find_show_by_tmdb_id(
                session, tmdb_id=episode.show_tmdb_id
            )

            if dry_run:
                if existing_show is None and episode.show_tmdb_id not in planned_shows:
                    planned_shows.add(episode.show_tmdb_id)
                    shows_created_count += 1
                linked_count += 1
                continue

            show = existing_show
            if show is None:
                show_media_item = media_item_repository.find_show_media_item_by_tmdb_id(
                    session, show_tmdb_id=episode.show_tmdb_id
                )
                show = ShowService.get_or_create_show(
                    session,
                    tmdb_id=episode.show_tmdb_id,
                    title=(
                        show_media_item.title
                        if show_media_item is not None
                        else f"show:{episode.show_tmdb_id}"
                    ),
                    year=show_media_item.year if show_media_item is not None else None,
                    tvdb_id=(
                        show_media_item.tvdb_id if show_media_item is not None else None
                    ),
                    imdb_id=(
                        show_media_item.imdb_id if show_media_item is not None else None
                    ),
                )
                shows_created_count += 1

            episode.show_id = show.show_id
            linked_count += 1

        if not dry_run and linked_count > 0:
            session.commit()

        return ShowBackfillResult(
            scanned_count=len(episodes),
            linked_count=linked_count,
            shows_created_count=shows_created_count,
            dry_run=dry_run,
        )
