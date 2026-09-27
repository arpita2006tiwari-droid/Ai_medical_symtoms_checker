import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.db.models.user import User

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user_email():
    return f"consultation_test_{uuid.uuid4()}@example.com"

@pytest.fixture(scope="module")
def test_password():
    return "StrongPass123!"

@pytest.fixture(scope="module", autouse=True)
def setup_teardown(test_user_email, test_password):
    # Setup
    response = client.post(
        "/api/auth/register",
        json={"email": test_user_email, "full_name": "Consultation Test User", "password": test_password}
    )
    yield
    # Teardown
    db = SessionLocal()
    user = db.query(User).filter(User.email == test_user_email).first()
    if user:
        from app.db.models.consultation import ConsultationPreparation
        db.query(ConsultationPreparation).filter(ConsultationPreparation.user_id == user.id).delete()
        db.delete(user)
        db.commit()
    db.close()

def get_auth_token(email, password):
    resp = client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    return resp.json()["access_token"]

def test_create_consultation_prep(test_user_email, test_password):
    token = get_auth_token(test_user_email, test_password)
    
    payload = {
        "main_concern": "Persistent back pain",
        "symptoms": "Lower back pain for 2 weeks",
        "questions": "Do I need an MRI?",
        "current_medicines": "Ibuprofen",
        "allergies": "None"
    }

    response = client.post(
        "/api/consultations", 
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["main_concern"] == "Persistent back pain"
    assert "id" in data

def test_create_consultation_prep_guest():
    payload = {
        "main_concern": "Persistent back pain",
        "symptoms": "Lower back pain for 2 weeks",
        "questions": "Do I need an MRI?",
        "current_medicines": "Ibuprofen",
        "allergies": "None"
    }

    # Guests should not be able to POST to the backend
    response = client.post("/api/consultations", json=payload)
    assert response.status_code == 401

def test_get_consultation_preps(test_user_email, test_password):
    token = get_auth_token(test_user_email, test_password)
    
    response = client.get("/api/consultations", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_data_isolation(test_user_email, test_password):
    token1 = get_auth_token(test_user_email, test_password)
    
    # Create prep as user 1
    resp1 = client.post(
        "/api/consultations", 
        json={"main_concern": "Private concern"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    prep_id = resp1.json()["id"]

    # Register and login user 2
    email2 = f"test2_{uuid.uuid4()}@example.com"
    pass2 = "Pass1234!"
    client.post("/api/auth/register", json={"email": email2, "full_name": "User 2", "password": pass2})
    token2 = get_auth_token(email2, pass2)

    # Attempt to read prep_id with user 2
    resp2 = client.get(f"/api/consultations/{prep_id}", headers={"Authorization": f"Bearer {token2}"})
    assert resp2.status_code == 404 # Backend filters by user_id so it returns 404

    # Cleanup user 2
    db = SessionLocal()
    user2 = db.query(User).filter(User.email == email2).first()
    if user2:
        from app.db.models.consultation import ConsultationPreparation
        db.query(ConsultationPreparation).filter(ConsultationPreparation.user_id == user2.id).delete()
        db.delete(user2)
        db.commit()
    db.close()
