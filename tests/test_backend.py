from fastapi.testclient import TestClient

import backend.main as backend_main


client = TestClient(backend_main.app)


def test_backend_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_backend_returns_validated_controller_reading(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "temperature": 29.5,
                "turbidity": 2.1,
                "tds": 190,
                "latitude": 26.45,
                "longitude": 80.33,
            }

    def fake_get(*args, **kwargs):
        assert kwargs["timeout"] == backend_main.REQUEST_TIMEOUT_SECONDS
        return FakeResponse()

    monkeypatch.setattr(backend_main.requests, "get", fake_get)

    response = client.get("/readings")
    assert response.status_code == 200
    assert response.json()["tds"] == 190


def test_backend_returns_502_when_controller_is_unavailable(monkeypatch):
    def fake_get(*args, **kwargs):
        raise backend_main.requests.ConnectionError("controller offline")

    monkeypatch.setattr(backend_main.requests, "get", fake_get)

    response = client.get("/readings")
    assert response.status_code == 502
