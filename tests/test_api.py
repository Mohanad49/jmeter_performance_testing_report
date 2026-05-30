from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint_returns_price():
    payload = {
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "mileage": 65000,
        "engine_size": 1.6,
        "transmission": "automatic",
        "fuel_type": "petrol",
    }
    response = client.post("/predict", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["prediction"]["estimated_price"] > 0
    assert body["prediction"]["lower_bound"] < body["prediction"]["estimated_price"]
    assert body["prediction"]["upper_bound"] > body["prediction"]["estimated_price"]
    assert body["processing_time_ms"] >= 0
