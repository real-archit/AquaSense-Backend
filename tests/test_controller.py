from fastapi.testclient import TestClient

from controller.controller import app


client = TestClient(app)


def test_controller_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_controller_reading_shape_and_ranges():
    response = client.get("/readings")
    assert response.status_code == 200
    payload = response.json()

    assert set(payload) == {"temperature", "turbidity", "tds", "latitude", "longitude"}
    assert 27.0 <= payload["temperature"] <= 32.0
    assert 1.0 <= payload["turbidity"] <= 4.0
    assert 150 <= payload["tds"] <= 250
    assert -90 <= payload["latitude"] <= 90
    assert -180 <= payload["longitude"] <= 180
