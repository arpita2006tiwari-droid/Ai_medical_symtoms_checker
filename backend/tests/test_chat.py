import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.llm_service import llm_service

client = TestClient(app)

def test_chat_integration_fallback():
    """Test 3, 5, 6, 7 — Endpoint integration and determinism preservation"""
    # Temporarily disable actual Gemini API calls to ensure test speed and CI independence
    original_client = llm_service.client
    llm_service.client = None 
    
    try:
        response = client.post(
            "/api/chat",
            json={"message": "I have severe chest pain and acidity"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify the ChatResponse schema encapsulates everything correctly
        assert "response" in data
        assert "not a medical diagnosis" in data["response"]
        
        # Verify ML predictions are entirely untampered
        assert len(data["predictions"]) > 0
        assert "model_probability" in data["predictions"][0]
        
        # Verify Urgency and Specialist logic persisted unchanged through the Chat route
        assert data["urgency"]["level"] == "urgent_attention"
        assert data["specialist_recommendation"]["specialist"] in ["Gastroenterologist", "Cardiologist"]
        
    finally:
        # Restore state
        llm_service.client = original_client

def test_chat_unknown_symptoms():
    """Test 8 — Unknown symptoms explicitly reported during chat"""
    original_client = llm_service.client
    llm_service.client = None 
    try:
        response = client.post(
            "/api/chat",
            json={"message": "I have headache and some madeupword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["unknown_symptoms"], list)
        assert "headache" in data["recognized_symptoms"]
    finally:
        llm_service.client = original_client
