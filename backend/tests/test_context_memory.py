import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_context_retrieval_and_isolation():
    # 1. Register/login User A
    email_a = f"contextA_{uuid.uuid4()}@example.com"
    password = "password123"
    client.post("/api/auth/register", json={"email": email_a, "password": password, "full_name": "Context User A"})
    login_res_a = client.post("/api/auth/login", json={"email": email_a, "password": password})
    assert login_res_a.status_code == 200, login_res_a.text
    token_a = login_res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register/login User B
    email_b = f"contextB_{uuid.uuid4()}@example.com"
    client.post("/api/auth/register", json={"email": email_b, "password": password, "full_name": "Context User B"})
    login_res_b = client.post("/api/auth/login", json={"email": email_b, "password": password})
    token_b = login_res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 2. Complete a pain assessment for User A
    pain_res_a = client.post("/api/pain-assessments", json={
        "body_region": "Leg",
        "pain_type": "Sharp",
        "severity": 8,
        "onset_duration": "Yesterday",
        "frequency": "Constant",
        "trend": "Worsening",
        "associated_symptoms": ["Swelling"],
        "notes": "Hurts when I walk"
    }, headers=headers_a)
    assert pain_res_a.status_code == 200

    # 3. User B should not see User A's pain assessments
    pain_list_b = client.get("/api/pain-assessments", headers=headers_b)
    assert len(pain_list_b.json()) == 0

    # 4. Start a chat for User A
    chat_res_a = client.post("/api/chat", json={"message": "My leg pain is getting worse."}, headers=headers_a)
    assert chat_res_a.status_code == 200
    conv_id_a = chat_res_a.json()["conversation_id"]
    assert conv_id_a is not None

    # 5. Start another conversation for User A (continuing)
    chat_res_a_cont = client.post("/api/chat", json={"message": "What about my leg pain?", "conversation_id": conv_id_a}, headers=headers_a)
    assert chat_res_a_cont.status_code == 200

    # 6. User B should not be able to get User A's conversation history
    conv_hist_b = client.get("/api/conversations", headers=headers_b)
    assert len(conv_hist_b.json()) == 0

    # 7. Guest User (No auth) checks
    chat_guest_res = client.post("/api/chat", json={"message": "My head hurts."})
    assert chat_guest_res.status_code == 200
    assert chat_guest_res.json()["conversation_id"] is None

    # Guest cannot fetch history
    hist_guest = client.get("/api/conversations")
    assert hist_guest.status_code == 401

    print("All isolation and context memory tests passed.")
