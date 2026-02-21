from fastapi.testclient import TestClient

from app.main import app


def test_root_frontend_serves_index() -> None:
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Klug Media" in response.text
