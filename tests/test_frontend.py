from fastapi.testclient import TestClient

from app.main import app


def test_root_frontend_serves_index() -> None:
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Klug Media" in response.text


def test_frontend_static_assets_are_served() -> None:
    client = TestClient(app)

    css_response = client.get("/web/styles.css")
    js_response = client.get("/web/app.js")

    assert css_response.status_code == 200
    assert ":root" in css_response.text
    assert js_response.status_code == 200
    assert "checkSession();" in js_response.text
