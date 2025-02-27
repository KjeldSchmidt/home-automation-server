from main import app
import pytest


@pytest.fixture()
def client():
    return app.test_client()


def test_web_root_page_returns_ok(client):
    response = client.get("/")
    assert response.status_code == 200
