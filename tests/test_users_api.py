from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.users import UserAlreadyExistsError, UserService


class DummyUser:
    def __init__(self, username: str) -> None:
        self.user_id = uuid4()
        self.username = username
        self.created_at = datetime.now(UTC)


def test_list_users_returns_users(monkeypatch) -> None:
    expected_user = DummyUser(username="alice")

    def fake_list_users(_session):
        return [expected_user]

    monkeypatch.setattr(UserService, "list_users", fake_list_users)

    client = TestClient(app)
    response = client.get("/api/v1/users")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["username"] == "alice"


def test_create_user_returns_201(monkeypatch) -> None:
    created_user = DummyUser(username="bob")

    def fake_create_user(_session, username: str):
        assert username == "bob"
        return created_user

    monkeypatch.setattr(UserService, "create_user", fake_create_user)

    client = TestClient(app)
    response = client.post("/api/v1/users", json={"username": "bob"})

    assert response.status_code == 201
    assert response.json()["username"] == "bob"


def test_create_user_duplicate_returns_409(monkeypatch) -> None:
    def fake_create_user(_session, _username: str):
        raise UserAlreadyExistsError("alice")

    monkeypatch.setattr(UserService, "create_user", fake_create_user)

    client = TestClient(app)
    response = client.post("/api/v1/users", json={"username": "alice"})

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
