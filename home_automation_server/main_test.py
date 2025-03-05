from flask.testing import FlaskClient

from home_automation_server.main import app
import pytest


@pytest.fixture()
def client() -> FlaskClient:
    return app.test_client()


def test_web_root_page_returns_ok(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
