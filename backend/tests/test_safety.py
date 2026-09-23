from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_safety_routine():
    """Test 1 — Routine"""
    # A symptom that is not in any safety rule
    response = client.post(
        "/api/predict",
        json={"symptoms": ["cough", "headache"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["urgency"] is not None
    assert data["urgency"]["level"] == "routine"
    assert len(data["urgency"]["matched_rules"]) == 0

def test_safety_medical_attention():
    """Test 2 — Medical attention"""
    # "palpitations" maps to medical_attention in our rules
    response = client.post(
        "/api/predict",
        json={"symptoms": ["palpitations"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["urgency"]["level"] == "medical_attention"
    assert len(data["urgency"]["matched_rules"]) > 0

def test_safety_urgent_attention():
    """Test 3 — Urgent attention"""
    # "chest pain" maps to urgent_attention
    response = client.post(
        "/api/predict",
        json={"symptoms": ["chest pain"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["urgency"]["level"] == "urgent_attention"
    assert any(rule["rule_id"] == "SR001" for rule in data["urgency"]["matched_rules"])

def test_safety_multiple_rules():
    """Test 4 — Multiple rules priority"""
    # Combine medical_attention ("loss of balance") and urgent_attention ("chest pain")
    response = client.post(
        "/api/predict",
        json={"symptoms": ["chest pain", "loss of balance"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["urgency"]["level"] == "urgent_attention"
    assert len(data["urgency"]["matched_rules"]) == 2

def test_safety_unknown_symptoms():
    """Test 5 — Unknown symptoms"""
    response = client.post(
        "/api/predict",
        json={"symptoms": ["made up symptom 123", "chest pain"]}
    )
    assert response.status_code == 200
    data = response.json()
    # Unknown symptoms don't crash and the valid one triggers urgency
    assert data["urgency"]["level"] == "urgent_attention"

def test_safety_duplicate_symptoms():
    """Test 6 — Duplicate symptoms"""
    response = client.post(
        "/api/predict",
        json={"symptoms": ["chest pain", "chest pain"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["urgency"]["level"] == "urgent_attention"
    # Should only trigger the rule once
    assert len(data["urgency"]["matched_rules"]) == 1

def test_safety_determinism():
    """Test 7 — Determinism"""
    r1 = client.post("/api/predict", json={"symptoms": ["coma"]})
    r2 = client.post("/api/predict", json={"symptoms": ["coma"]})
    
    assert r1.json()["urgency"] == r2.json()["urgency"]

def test_safety_ml_independence():
    """Test 8 — ML independence and backward compatibility"""
    response = client.post(
        "/api/predict",
        json={"symptoms": ["high fever", "cough", "headache"]}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Assert ML output is untouched
    assert len(data["predictions"]) == 3
    assert "model_probability" in data["predictions"][0]
    
    # And urgency is evaluated cleanly alongside it
    assert data["urgency"]["level"] == "routine"
