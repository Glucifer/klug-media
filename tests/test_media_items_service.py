from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.media_items import MediaItemAlreadyExistsError, MediaItemService


def test_create_media_item_strips_values(monkeypatch) -> None:
    session = Mock()
    expected_item = Mock()

    def fake_create_media_item(_session, **kwargs):
        assert kwargs["title"] == "Alien"
        assert kwargs["imdb_id"] == "tt0078748"
        return expected_item

    monkeypatch.setattr(
        "app.services.media_items.media_item_repository.create_media_item",
        fake_create_media_item,
    )

    item = MediaItemService.create_media_item(
        session,
        media_type="movie",
        title="  Alien  ",
        year=1979,
        tmdb_id=348,
        imdb_id="  tt0078748  ",
        tvdb_id=None,
    )

    assert item is expected_item
    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_create_media_item_empty_title_raises_value_error() -> None:
    session = Mock()

    with pytest.raises(ValueError):
        MediaItemService.create_media_item(
            session,
            media_type="movie",
            title="   ",
            year=None,
            tmdb_id=None,
            imdb_id=None,
            tvdb_id=None,
        )


def test_create_media_item_integrity_error_maps_to_domain_error(monkeypatch) -> None:
    session = Mock()

    def fake_create_media_item(_session, **_kwargs):
        raise IntegrityError("insert", {}, Exception("duplicate"))

    monkeypatch.setattr(
        "app.services.media_items.media_item_repository.create_media_item",
        fake_create_media_item,
    )

    with pytest.raises(MediaItemAlreadyExistsError):
        MediaItemService.create_media_item(
            session,
            media_type="movie",
            title="Alien",
            year=None,
            tmdb_id=None,
            imdb_id=None,
            tvdb_id=None,
        )

    session.rollback.assert_called_once()
