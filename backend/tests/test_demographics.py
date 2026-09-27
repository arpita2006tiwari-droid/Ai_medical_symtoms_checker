from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_adult_age_skipped():
    """Test that a user can skip adult age and still get a prediction."""
    response = client.post("/api/predict", json={
        "symptoms": ["headache", "fever"],
        # No age, gender, or patient_type
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "predictions" in data
    # At least one prediction if ML is loaded
    assert len(data["predictions"]) > 0

def test_newborn_age_required():
    """Test that if patient_type is newborn, age is required."""
    response = client.post("/api/predict", json={
        "symptoms": ["fever"],
        "patient_type": "newborn"
        # Missing age
    })
    # Should fail pydantic validation
    assert response.status_code == 422
    data = response.json()
    assert any("Age is required for newborn patient type" in error["msg"] for error in data["detail"])

def test_newborn_ml_bypass():
    """Test that newborns bypass the ML model and get pediatric recommendations."""
    response = client.post("/api/predict", json={
        "symptoms": ["fever"],
        "patient_type": "newborn",
        "age": 2,
        "age_unit": "months"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["predictions"]) == 0
    assert data["specialist_recommendation"]["specialist"] == "Pediatrician"
    assert "not designed for newborns" in data["disclaimer"]

def test_guest_access():
    """Test that guest access (no auth) works."""
    # Already doing this implicitly above, but explicitly asserting no token needed
    response = client.post("/api/predict", json={
        "symptoms": ["headache"]
    })
    assert response.status_code == 200

def test_safety_behavior_missing_demographics():
    """Test that severe symptoms trigger high urgency even without demographics."""
    response = client.post("/api/predict", json={
        "symptoms": ["chest pain"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["urgency"]["level"] == "urgent_attention"
