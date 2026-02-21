from app.db.base import Base
from app.db.models import entities  # noqa: F401


def test_baseline_tables_registered() -> None:
    expected_tables = {
        "app.import_batch",
        "app.import_batch_error",
        "app.media_item",
        "app.media_version",
        "app.shows",
        "app.tag",
        "app.tmdb_metadata_cache",
        "app.users",
        "app.watch_event",
        "app.watch_event_tag",
    }
    assert expected_tables.issubset(Base.metadata.tables.keys())
