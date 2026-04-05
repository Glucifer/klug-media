from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.db.models.entities import CollectionEntry, Show


def test_collection_entry_schema_allows_nullable_show_tmdb_and_persists_entries(
    integration_session_factory: sessionmaker[Session],
) -> None:
    session = integration_session_factory()
    show = Show(
        tmdb_id=None,
        tvdb_id=12345,
        imdb_id=None,
        title="Unmatched Show",
        year=2024,
    )
    session.add(show)
    session.commit()
    session.refresh(show)

    entry = CollectionEntry(
        source="jellyfin",
        source_item_id="jf-show-1",
        item_type="show",
        show_id=show.show_id,
        library_id="tv",
        library_name="TV Shows",
    )
    session.add(entry)
    session.commit()

    tmdb_is_nullable = session.execute(
        text(
            """
            SELECT is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'app'
              AND table_name = 'shows'
              AND column_name = 'tmdb_id'
            """
        )
    ).scalar_one()

    assert tmdb_is_nullable == "YES"
    assert entry.collection_entry_id is not None
    session.close()
