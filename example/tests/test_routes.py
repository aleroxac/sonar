import pytest
from src.main import app


@pytest.fixture
def client():
    client = app.test_client()
    yield client


def test_request_example(client):
    response = client.get("/status")
    assert response.json == {"status": "UP"}
    assert response.status_code == 200
