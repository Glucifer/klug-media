from fastapi.testclient import TestClient

from app.main import app


def test_root_frontend_serves_index() -> None:
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Klug Media" in response.text
    assert "Library" in response.text
    assert "Watched Media Index" in response.text
    assert "Back to Library" in response.text
    assert "Open History" in response.text
    assert "Needs Attention" in response.text
    assert "Back to Dashboard" in response.text
    assert "Completion percentages come later with Collection." in response.text
    assert "Tracked Shows" in response.text
    assert "Analytics" in response.text
    assert "Year-over-Year Summary" in response.text
    assert "Open Selected Year Log" in response.text
    assert "Selected Year Drilldown" in response.text
    assert "Title Matrix" in response.text
    assert "Filter titles" in response.text
    assert "Selected Year Count" in response.text
    assert "Decade Matrix" in response.text
    assert "Analytics Drilldown" in response.text
    assert "Click any non-zero count to inspect the matching Horrorfest watches." in response.text
    assert "Decade labels and non-zero cells open the same shared drilldown panel." in response.text
    assert "Open Log Year" in response.text
    assert "Clear Drilldown" in response.text
    assert "Select a title, decade, or breakdown count to inspect the matching Horrorfest watches." in response.text
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
