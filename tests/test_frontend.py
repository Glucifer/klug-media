from fastapi.testclient import TestClient

from app.main import app


def test_root_frontend_serves_index() -> None:
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Klug Media" in response.text
    assert "Recent Watch History" in response.text
    assert "Import Watch History" in response.text
    assert "Use Latest Cursor" in response.text
    assert "Import History" in response.text
    assert "Clear Filter" in response.text
    assert "Select an import batch to view details." in response.text
    assert "Copy Detail JSON" in response.text
    assert "Download Errors JSON" in response.text
    assert "completed_with_errors" in response.text
    assert "API Health:" in response.text
    assert "Last Refresh:" in response.text


def test_frontend_static_assets_are_served() -> None:
    client = TestClient(app)

    css_response = client.get("/web/styles.css")
    js_response = client.get("/web/app.js")

    assert css_response.status_code == 200
    assert ":root" in css_response.text
    assert js_response.status_code == 200
    assert "checkSession();" in js_response.text
