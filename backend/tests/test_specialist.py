from fastapi.testclient import TestClient
from app.main import app
from app.services.specialist_service import specialist_service

client = TestClient(app)

def test_specialist_exact_mapping():
    """Test 1 — Exact condition mapping"""
    # Force a prediction for GERD which maps to Gastroenterologist
    # stomach pain + acidity commonly triggers GERD in this dataset
    response = client.post(
        "/api/predict",
        json={"symptoms": ["stomach pain", "acidity"]}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["specialist_recommendation"]["specialist"] == "Gastroenterologist"
    assert data["specialist_recommendation"]["basis"] == "predicted_condition"

def test_specialist_fallback():
    """Test 2 — General Physician fallback for unmapped conditions"""
    # Directly unit test the service for an unmapped condition
    rec = specialist_service.recommend("Completely Unknown Condition 123")
    assert rec.specialist == "General Physician"
    assert rec.basis == "general_fallback"

def test_specialist_empty_input():
    """Test 4 — Empty input"""
    rec = specialist_service.recommend(None)
    assert rec.specialist == "General Physician"
    assert rec.basis == "general_fallback"

def test_specialist_determinism():
    """Test 6 — Determinism"""
    r1 = client.post("/api/predict", json={"symptoms": ["chest pain"]})
    r2 = client.post("/api/predict", json={"symptoms": ["chest pain"]})
    
    assert r1.json()["specialist_recommendation"] == r2.json()["specialist_recommendation"]

def test_specialist_ml_independence():
    """Test 8 — ML independence and backward compatibility"""
    response = client.post(
        "/api/predict",
        json={"symptoms": ["high fever", "cough", "headache"]}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Assert ML output is completely untouched
    assert len(data["predictions"]) == 3
    assert "model_probability" in data["predictions"][0]
    
    # Verify the new keys exist seamlessly alongside
    assert "specialist_recommendation" in data
    assert data["specialist_recommendation"]["specialist"] is not None

def test_provider_endpoint():
    """Verify POST /api/providers/info works without external APIs"""
    response = client.post("/api/providers/info")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False
    assert "message" in data
