from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from unittest.mock import Mock

from app.services.media_enrichment import MediaEnrichmentService


def _make_media_item(**overrides):
    payload = {
        "media_item_id": uuid4(),
        "type": "movie",
        "title": "Alien",
        "year": 1979,
        "summary": None,
        "poster_url": None,
        "release_date": None,
        "tmdb_id": None,
        "imdb_id": "tt0078748",
        "tvdb_id": None,
        "show_tmdb_id": None,
        "season_number": None,
        "episode_number": None,
        "show_id": None,
        "base_runtime_seconds": None,
        "metadata_source": None,
        "metadata_updated_at": None,
        "enrichment_status": "pending",
        "enrichment_error": None,
        "enrichment_attempted_at": None,
        "created_at": datetime.now(UTC),
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def test_enrich_movie_resolves_tmdb_id_from_imdb(monkeypatch) -> None:
    session = Mock()
    media_item = _make_media_item()
    updated_item = _make_media_item(tmdb_id=348, enrichment_status="enriched")

    monkeypatch.setattr(
        "app.services.media_enrichment.MediaItemService.get_media_item",
        lambda *_args, **_kwargs: media_item,
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.is_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.find_by_external_id",
        lambda *_args, **_kwargs: SimpleNamespace(tmdb_id=348, media_type="movie", payload={}),
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.get_movie_details",
        lambda *_args, **_kwargs: {
            "title": "Alien",
            "overview": "In space, no one can hear you scream.",
            "poster_path": "/poster.jpg",
            "release_date": "1979-05-25",
            "runtime": 117,
        },
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.MediaItemService.update_media_item_metadata",
        lambda *_args, **kwargs: updated_item if kwargs["tmdb_id"] == 348 else None,
    )

    result = MediaEnrichmentService.retry_media_item(
        session,
        media_item_id=media_item.media_item_id,
    )

    assert result.action == "enriched"
    assert result.media_item.tmdb_id == 348
    session.commit.assert_called_once()


def test_enrich_episode_resolves_show_tmdb_id_from_tvdb(monkeypatch) -> None:
    session = Mock()
    media_item = _make_media_item(
        type="episode",
        title="Pilot",
        imdb_id=None,
        tvdb_id=12345,
        season_number=1,
        episode_number=1,
    )
    updated_item = _make_media_item(
        type="episode",
        title="Pilot",
        show_tmdb_id=204154,
        tvdb_id=12345,
        season_number=1,
        episode_number=1,
        enrichment_status="enriched",
    )

    monkeypatch.setattr(
        "app.services.media_enrichment.MediaItemService.get_media_item",
        lambda *_args, **_kwargs: media_item,
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.is_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.find_by_external_id",
        lambda *_args, **_kwargs: SimpleNamespace(
            tmdb_id=166773,
            media_type="tv_episode",
            payload={},
            resolved_show_tmdb_id=204154,
        ),
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.get_tv_details",
        lambda *_args, **_kwargs: {
            "name": "FROM",
            "first_air_date": "2022-02-20",
        },
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.get_episode_details",
        lambda *_args, **_kwargs: {
            "name": "Long Day's Journey Into Night",
            "overview": "Episode summary",
            "air_date": "2022-02-20",
            "runtime": 52,
            "still_path": "/still.jpg",
        },
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.ShowService.upsert_show",
        lambda *_args, **_kwargs: SimpleNamespace(show_id=uuid4()),
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.MediaItemService.update_media_item_metadata",
        lambda *_args, **kwargs: updated_item if kwargs["show_tmdb_id"] == 204154 else None,
    )

    result = MediaEnrichmentService.retry_media_item(
        session,
        media_item_id=media_item.media_item_id,
    )

    assert result.action == "enriched"
    assert result.media_item.show_tmdb_id == 204154
    session.commit.assert_called_once()


def test_retry_marks_failure_without_breaking(monkeypatch) -> None:
    session = Mock()
    media_item = _make_media_item()
    failed_item = _make_media_item(enrichment_status="failed", enrichment_error="boom")

    monkeypatch.setattr(
        "app.services.media_enrichment.MediaItemService.get_media_item",
        lambda *_args, **_kwargs: media_item,
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.is_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.TmdbService.find_by_external_id",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    monkeypatch.setattr(
        "app.services.media_enrichment.MediaItemService.update_media_item_metadata",
        lambda *_args, **_kwargs: failed_item,
    )

    result = MediaEnrichmentService.retry_media_item(
        session,
        media_item_id=media_item.media_item_id,
    )

    assert result.action == "failed"
    assert result.reason == "boom"
    session.commit.assert_called_once()
