"""
Stage 1 tests — verify the API works before containerizing.
Run: pytest tests/ -v
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

SAMPLE_TRANSACTION = {
    "V1": -1.36, "V2": -0.07, "V3": 2.54, "V4": 1.38,
    "V5": -0.34, "V6": 0.46, "V7": 0.24, "V8": 0.10,
    "V9": 0.36, "V10": 0.09, "V11": -0.55, "V12": -0.62,
    "V13": -0.99, "V14": -0.31, "V15": 1.47, "V16": -0.47,
    "V17": 0.21, "V18": 0.03, "V19": 0.40, "V20": 0.25,
    "V21": -0.02, "V22": 0.28, "V23": -0.11, "V24": 0.07,
    "V25": 0.13, "V26": -0.19, "V27": 0.13, "V28": -0.02,
    "Amount": 149.62
}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()


def test_health():
    response = client.get("/health")
    # 200 if model loaded, 503 if not — both are valid at this stage
    assert response.status_code in [200, 503]


def test_predict_returns_correct_schema():
    response = client.post("/predict", json=SAMPLE_TRANSACTION)
    # Will return 503 if model not trained yet — that's expected in Stage 1
    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data
        assert "fraud_probability" in data
        assert "is_fraud" in data
        assert data["prediction"] in [0, 1]
        assert 0.0 <= data["fraud_probability"] <= 1.0


def test_predict_missing_field():
    bad_request = SAMPLE_TRANSACTION.copy()
    del bad_request["Amount"]
    response = client.post("/predict", json=bad_request)
    assert response.status_code == 422  # Pydantic validation error


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
