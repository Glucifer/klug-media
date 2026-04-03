from __future__ import annotations

import argparse

from sqlalchemy import select

from app.db.models.entities import WatchEvent
from app.db.session import SessionLocal
from app.services.watch_events import WatchEventService


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recompute watch-event rewatch flags from each media timeline."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the number of affected user/media timelines without writing changes.",
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    session = SessionLocal()

    try:
        timeline_keys = list(
            session.execute(
                select(WatchEvent.user_id, WatchEvent.media_item_id).distinct()
            ).all()
        )

        for user_id, media_item_id in timeline_keys:
            WatchEventService._recompute_rewatch_for_media_timeline(
                session,
                user_id=user_id,
                media_item_id=media_item_id,
            )

        if args.dry_run:
            session.rollback()
            print(
                f"Would recompute rewatch flags for {len(timeline_keys)} user/media timelines."
            )
        else:
            session.commit()
            print(
                f"Recomputed rewatch flags for {len(timeline_keys)} user/media timelines."
            )
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(run())
