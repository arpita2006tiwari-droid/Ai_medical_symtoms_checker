from fastapi.testclient import TestClient
from app.main import app
import pytest

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_predict_valid_symptoms(client):
    response = client.post("/api/predict", json={"symptoms": ["high fever", "cough", "headache"]})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "predictions" in data
    assert len(data["predictions"]) <= 3
    
    # Check that model probabilities are numeric and descending
    probs = [p["model_probability"] for p in data["predictions"]]
    assert all(isinstance(p, float) for p in probs)
    assert probs == sorted(probs, reverse=True)
    
    # Check descriptions and precautions (Test 1 & 2)
    for pred in data["predictions"]:
        assert "description" in pred
        assert "precautions" in pred
        assert isinstance(pred["precautions"], list)

    # Check severities (Test 3)
    assert "symptom_severity" in data
    assert len(data["symptom_severity"]) > 0
    # "cough" and "headache" are in recognized symptoms
    symptoms_with_severity = [s["symptom"] for s in data["symptom_severity"]]
    assert "cough" in symptoms_with_severity
    assert "headache" in symptoms_with_severity
    assert "high fever" in symptoms_with_severity

def test_predict_unknown_symptoms(client):
    response = client.post("/api/predict", json={"symptoms": ["high fever", "random unknown symptom"]})
    assert response.status_code == 200
    data = response.json()
    assert "random unknown symptom" in data["unknown_symptoms"]
    assert "high fever" in data["recognized_symptoms"]
    
    # Test 4 - unknown symptom does not appear in severity
    symptoms_with_severity = [s["symptom"] for s in data["symptom_severity"]]
    assert "random unknown symptom" not in symptoms_with_severity

def test_predict_empty_list(client):
    response = client.post("/api/predict", json={"symptoms": []})
    assert response.status_code == 422 # Pydantic validation error

def test_predict_invalid_empty_strings(client):
    response = client.post("/api/predict", json={"symptoms": ["  ", ""]})
    assert response.status_code == 422

def test_predict_identical_to_phase2a(client):
    # Test 5 - Prediction values unchanged
    response = client.post("/api/predict", json={"symptoms": ["high fever", "cough", "headache"]})
    data = response.json()
    preds = data["predictions"]
    
    # Should match exactly the Phase 2A output
    assert preds[0]["condition"] == "Bronchial Asthma"
    assert abs(preds[0]["model_probability"] - 0.26) < 0.01
    assert preds[1]["condition"] == "Paralysis (brain hemorrhage)"
    assert abs(preds[1]["model_probability"] - 0.17) < 0.01
    assert preds[2]["condition"] == "Hypertension"
    assert abs(preds[2]["model_probability"] - 0.11) < 0.01

def test_predict_missing_information(client):
    # Test 6 - Missing information handles safely
    # For a completely unknown prediction condition (simulate by directly calling the service)
    from app.services.medical_info_service import medical_info_service
    desc = medical_info_service.get_description("Nonexistent Disease")
    assert desc is None
    precs = medical_info_service.get_precautions("Nonexistent Disease")
    assert precs == []

def test_predict_remains_unchanged(client):
    """Test 7 — Existing structured prediction remains unchanged"""
    response = client.post(
        "/api/predict",
        json={"symptoms": ["high fever", "cough", "headache"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "symptoms" in data["input"]
    assert data["predictions"][0]["condition"] == "Bronchial Asthma"
    assert data["predictions"][0]["model_probability"] == 0.26

def test_analyze_end_to_end(client):
    """Test 8 — End-to-end /api/analyze"""
    response = client.post(
        "/api/analyze",
        json={"text": "I have a high fever, cough and headache."}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    # 1. symptoms are extracted and passed (reflected in recognized_symptoms)
    assert "high fever" in data["recognized_symptoms"]
    # 2. extracted symptoms are passed to ML
    assert data["input"] == {"text": "I have a high fever, cough and headache."}
    # 3. top predictions are returned (should match structured exactly)
    assert len(data["predictions"]) == 3
    assert data["predictions"][0]["condition"] == "Bronchial Asthma"
    assert data["predictions"][0]["model_probability"] == 0.26
    # 4. descriptions are returned
    assert data["predictions"][0]["description"] is not None
    # 5. precautions are returned
    assert isinstance(data["predictions"][0]["precautions"], list)
    assert len(data["predictions"][0]["precautions"]) > 0
    # 6. severity information is returned
    assert len(data["symptom_severity"]) >= 3
    # 7. disclaimer remains present
    assert "preliminary information only" in data["disclaimer"]
