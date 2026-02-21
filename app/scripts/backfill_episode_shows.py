from __future__ import annotations

import argparse

from app.db.session import SessionLocal
from app.services.show_backfill import ShowBackfillService


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill episode media_item.show_id links from show_tmdb_id."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be linked/created without writing changes.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of episode rows to process.",
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.limit is not None and args.limit <= 0:
        print("--limit must be greater than zero")
        return 2

    session = SessionLocal()
    try:
        result = ShowBackfillService.backfill_episode_show_links(
            session,
            dry_run=args.dry_run,
            limit=args.limit,
        )
    except Exception as exc:
        print(f"Backfill failed: {exc}")
        return 1
    finally:
        session.close()

    print("Episode show-link backfill summary")
    print(f"  dry_run: {result.dry_run}")
    print(f"  scanned: {result.scanned_count}")
    print(f"  linked: {result.linked_count}")
    print(f"  shows_created: {result.shows_created_count}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
