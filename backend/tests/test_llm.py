import pytest
from app.services.llm_service import llm_service
from app.schemas import PredictionResponse

@pytest.fixture
def dummy_context():
    return PredictionResponse(
        success=True,
        input={"symptoms": ["chest pain"]},
        recognized_symptoms=["chest pain"],
        unknown_symptoms=[],
        predictions=[
            {
                "condition": "Heart attack",
                "model_probability": 0.88,
                "description": "...",
                "precautions": ["..."]
            }
        ],
        symptom_severity=[{"symptom": "chest pain", "severity": 7}],
        urgency={
            "level": "urgent_attention",
            "message": "Prompt medical attention is recommended.",
            "matched_rules": []
        },
        specialist_recommendation={
            "specialist": "Cardiologist",
            "reason": "...",
            "basis": "predicted_condition",
            "condition": "Heart attack"
        }
    )

def test_llm_fallback_generation(dummy_context):
    """Test 1 & 4 — Fallback behavior without Gemini API key"""
    # Force client to None to simulate failure or missing key
    llm_service.client = None 
    
    response_text = llm_service.generate_response("I have chest pain", dummy_context)
    
    # Must include deterministic medical fallback data securely
    assert "not a medical diagnosis" in response_text
    assert "Cardiologist" in response_text
    assert "Prompt medical attention" in response_text
