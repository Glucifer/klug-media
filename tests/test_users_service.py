from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.users import (
    JellyfinUserAlreadyMappedError,
    UserAlreadyExistsError,
    UserService,
)


def test_create_user_strips_whitespace(monkeypatch) -> None:
    session = Mock()
    expected_user = Mock()

    def fake_create_user(_session, username: str, timezone: str):
        assert username == "alice"
        assert timezone == "UTC"
        return expected_user

    monkeypatch.setattr(
        "app.services.users.user_repository.create_user", fake_create_user
    )

    user = UserService.create_user(session, "  alice  ")

    assert user is expected_user
    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_create_user_empty_raises_value_error() -> None:
    session = Mock()

    with pytest.raises(ValueError):
        UserService.create_user(session, "   ")


def test_create_user_integrity_error_maps_to_domain_error(monkeypatch) -> None:
    session = Mock()

    def fake_create_user(_session, _username: str, _timezone: str):
        raise IntegrityError("insert", {}, Exception("duplicate"))

    monkeypatch.setattr(
        "app.services.users.user_repository.create_user", fake_create_user
    )

    with pytest.raises(UserAlreadyExistsError):
        UserService.create_user(session, "alice")

    session.rollback.assert_called_once()


def test_create_user_strips_timezone_whitespace(monkeypatch) -> None:
    session = Mock()
    expected_user = Mock()

    def fake_create_user(_session, username: str, timezone: str):
        assert username == "alice"
        assert timezone == "America/Edmonton"
        return expected_user

    monkeypatch.setattr(
        "app.services.users.user_repository.create_user", fake_create_user
    )

    user = UserService.create_user(session, "alice", "  America/Edmonton  ")

    assert user is expected_user


def test_create_user_empty_timezone_raises_value_error() -> None:
    session = Mock()

    with pytest.raises(ValueError):
        UserService.create_user(session, "alice", "   ")


def test_update_jellyfin_mapping_commits(monkeypatch) -> None:
    session = Mock()
    user = Mock()
    jellyfin_user_id = uuid4()
    monkeypatch.setattr(
        "app.services.users.user_repository.get_user_by_id",
        lambda *_args, **_kwargs: user,
    )
    monkeypatch.setattr(
        "app.services.users.user_repository.update_jellyfin_user_mapping",
        lambda *_args, **_kwargs: user,
    )

    result = UserService.update_jellyfin_user_mapping(
        session,
        user_id=uuid4(),
        jellyfin_user_id=jellyfin_user_id,
    )

    assert result is user
    session.commit.assert_called_once()


def test_update_jellyfin_mapping_maps_integrity_error(monkeypatch) -> None:
    session = Mock()
    monkeypatch.setattr(
        "app.services.users.user_repository.get_user_by_id",
        lambda *_args, **_kwargs: Mock(),
    )

    def fail_update(*_args, **_kwargs):
        raise IntegrityError("update", {}, Exception("duplicate"))

    monkeypatch.setattr(
        "app.services.users.user_repository.update_jellyfin_user_mapping",
        fail_update,
    )

    with pytest.raises(JellyfinUserAlreadyMappedError):
        UserService.update_jellyfin_user_mapping(
            session,
            user_id=uuid4(),
            jellyfin_user_id=uuid4(),
        )

    session.rollback.assert_called_once()
