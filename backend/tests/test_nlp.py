from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_extract_symptoms_basic():
    """Test 1 — Basic natural language"""
    response = client.post(
        "/api/extract-symptoms",
        json={"text": "I have a high fever, cough and headache."}
    )
    assert response.status_code == 200
    data = response.json()
    symptoms = data["recognized_symptoms"]
    assert "high fever" in symptoms
    assert "cough" in symptoms
    assert "headache" in symptoms
    assert data["symptom_count"] >= 3

def test_extract_symptoms_case_insensitive():
    """Test 2 — Case insensitive"""
    response = client.post(
        "/api/extract-symptoms",
        json={"text": "I HAVE HIGH FEVER AND COUGH."}
    )
    assert response.status_code == 200
    symptoms = response.json()["recognized_symptoms"]
    assert "high fever" in symptoms
    assert "cough" in symptoms

def test_extract_symptoms_punctuation():
    """Test 3 — Punctuation"""
    response = client.post(
        "/api/extract-symptoms",
        json={"text": "High fever, cough, headache."}
    )
    assert response.status_code == 200
    symptoms = response.json()["recognized_symptoms"]
    assert "high fever" in symptoms
    assert "cough" in symptoms
    assert "headache" in symptoms

def test_extract_symptoms_duplicates():
    """Test 4 — Duplicate symptoms"""
    response = client.post(
        "/api/extract-symptoms",
        json={"text": "I have cough and cough with high fever."}
    )
    assert response.status_code == 200
    symptoms = response.json()["recognized_symptoms"]
    assert symptoms.count("cough") == 1
    assert symptoms.count("high fever") == 1
    assert len(symptoms) == 2

def test_extract_symptoms_unsupported_generic():
    """Test 5 — Unsupported generic symptom (fever doesn't become high fever)"""
    response = client.post(
        "/api/extract-symptoms",
        json={"text": "I have fever."}
    )
    assert response.status_code == 200
    # The existing vocabulary has 'high fever' and 'mild fever' but not 'fever'.
    # If the regex is strictly matching boundaries, it should not extract anything.
    symptoms = response.json()["recognized_symptoms"]
    assert "high fever" not in symptoms
    assert "mild fever" not in symptoms
    assert "fever" not in symptoms

def test_extract_symptoms_no_recognizable():
    """Test 6 — No recognizable symptoms"""
    response = client.post(
        "/api/extract-symptoms",
        json={"text": "I don't feel well today."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recognized_symptoms"] == []
    assert data["symptom_count"] == 0

def test_analyze_natural_language_no_symptoms_422():
    """Test /api/analyze throws 422 if no symptoms extracted"""
    response = client.post(
        "/api/analyze",
        json={"text": "I don't feel well today."}
    )
    assert response.status_code == 422
    assert "No recognized symptoms found" in response.json()["detail"]
