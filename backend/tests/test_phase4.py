import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.db.models.user import User

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user_email():
    return f"test_{uuid.uuid4()}@example.com"

@pytest.fixture(scope="module")
def test_password():
    return "StrongPass123!"

@pytest.fixture(scope="module", autouse=True)
def cleanup(test_user_email):
    yield
    # Cleanup after all tests in this module
    db = SessionLocal()
    user = db.query(User).filter(User.email == test_user_email).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()

def test_user_registration(test_user_email, test_password):
    response = client.post(
        "/api/auth/register",
        json={"email": test_user_email, "full_name": "Test User", "password": test_password}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_email
    assert "id" in data
    assert "hashed_password" not in data

def test_duplicate_registration(test_user_email, test_password):
    response = client.post(
        "/api/auth/register",
        json={"email": test_user_email, "full_name": "Test User", "password": test_password}
    )
    assert response.status_code == 400

def test_login_success(test_user_email, test_password):
    response = client.post(
        "/api/auth/login",
        json={"email": test_user_email, "password": test_password}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(test_user_email):
    response = client.post(
        "/api/auth/login",
        json={"email": test_user_email, "password": "WrongPassword!"}
    )
    assert response.status_code == 401

def test_get_me_unauthorized():
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_get_me_authorized(test_user_email, test_password):
    # Login to get token
    login_resp = client.post(
        "/api/auth/login",
        json={"email": test_user_email, "password": test_password}
    )
    token = login_resp.json()["access_token"]
    
    # Get me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == test_user_email

def test_analysis_saved_for_authenticated_user(test_user_email, test_password):
    login_resp = client.post(
        "/api/auth/login",
        json={"email": test_user_email, "password": test_password}
    )
    token = login_resp.json()["access_token"]

    # Predict with auth
    predict_resp = client.post(
        "/api/predict",
        json={"symptoms": ["headache", "fever"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert predict_resp.status_code == 200
    
    # Get history
    history_resp = client.get("/api/history", headers={"Authorization": f"Bearer {token}"})
    assert history_resp.status_code == 200
    history_data = history_resp.json()
    
    assert len(history_data) >= 1
    assert "headache" in history_data[0]["recognized_symptoms"]
    assert history_data[0]["analysis_source"] == "predict"

def test_anonymous_prediction_still_works():
    predict_resp = client.post(
        "/api/predict",
        json={"symptoms": ["headache", "fever"]}
    )
    assert predict_resp.status_code == 200
    assert predict_resp.json()["success"] == True

def test_conversation_saved_for_authenticated_user(test_user_email, test_password):
    login_resp = client.post(
        "/api/auth/login",
        json={"email": test_user_email, "password": test_password}
    )
    token = login_resp.json()["access_token"]

    # Prevent actual Gemini call to save time/tokens if LLMService defaults to fallback without key
    # Chat endpoint
    chat_resp = client.post(
        "/api/chat",
        json={"message": "I have a headache and a fever"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert chat_resp.status_code == 200
    
    # Check conversations
    convs_resp = client.get("/api/conversations", headers={"Authorization": f"Bearer {token}"})
    assert convs_resp.status_code == 200
    convs_data = convs_resp.json()
    assert len(convs_data) >= 1
    
    # Check messages in that conversation
    conv_id = convs_data[0]["id"]
    conv_resp = client.get(f"/api/conversations/{conv_id}", headers={"Authorization": f"Bearer {token}"})
    assert conv_resp.status_code == 200
    assert len(conv_resp.json()["messages"]) == 2 # 1 user, 1 assistant
