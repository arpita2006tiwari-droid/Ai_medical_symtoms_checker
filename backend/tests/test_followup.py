from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_followup_start():
    """Test 1 — Start follow-up"""
    response = client.post(
        "/api/follow-up/start",
        json={"symptoms": ["high fever", "cough"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["recognized_symptoms"] == ["high fever", "cough"]
    assert data["complete"] is False
    assert data["question"] is not None
    assert data["question"]["id"] not in ["high fever", "cough"]

def test_followup_no_duplicate_known_symptom():
    """Test 2 — No duplicate known symptom"""
    response = client.post(
        "/api/follow-up/start",
        json={"symptoms": ["headache"]}
    )
    assert response.status_code == 200
    data = response.json()
    # It should ask something else, never headache
    assert data["question"]["id"] != "headache"

def test_followup_yes_answer():
    """Test 3 — Yes answer"""
    # Start
    start_resp = client.post("/api/follow-up/start", json={"symptoms": ["high fever"]})
    state = start_resp.json()["state"]
    q_id = start_resp.json()["question"]["id"]
    
    # Answer Yes
    ans_resp = client.post(
        "/api/follow-up/answer",
        json={
            "state": state,
            "question_id": q_id,
            "answer": "yes"
        }
    )
    assert ans_resp.status_code == 200
    new_state = ans_resp.json()["state"]
    assert q_id in new_state["recognized_symptoms"]
    assert new_state["answers"][q_id] is True

def test_followup_no_answer():
    """Test 4 — No answer"""
    start_resp = client.post("/api/follow-up/start", json={"symptoms": ["high fever"]})
    state = start_resp.json()["state"]
    q_id = start_resp.json()["question"]["id"]
    
    ans_resp = client.post(
        "/api/follow-up/answer",
        json={
            "state": state,
            "question_id": q_id,
            "answer": "no"
        }
    )
    new_state = ans_resp.json()["state"]
    assert q_id not in new_state["recognized_symptoms"]
    assert new_state["answers"][q_id] is False

def test_followup_natural_yes():
    """Test 5 — Natural-language yes"""
    start_resp = client.post("/api/follow-up/start", json={"symptoms": ["high fever"]})
    state = start_resp.json()["state"]
    q_id = start_resp.json()["question"]["id"]
    
    ans_resp = client.post(
        "/api/follow-up/answer",
        json={
            "state": state,
            "question_id": q_id,
            "answer": "Yes, I have it."
        }
    )
    new_state = ans_resp.json()["state"]
    assert q_id in new_state["recognized_symptoms"]
    assert new_state["answers"][q_id] is True

def test_followup_natural_no():
    """Test 6 — Natural-language no"""
    start_resp = client.post("/api/follow-up/start", json={"symptoms": ["high fever"]})
    state = start_resp.json()["state"]
    q_id = start_resp.json()["question"]["id"]
    
    ans_resp = client.post(
        "/api/follow-up/answer",
        json={
            "state": state,
            "question_id": q_id,
            "answer": "No, I don't have it."
        }
    )
    new_state = ans_resp.json()["state"]
    assert q_id not in new_state["recognized_symptoms"]
    assert new_state["answers"][q_id] is False

def test_followup_free_text_additional():
    """Test 7 — Free-text additional symptom"""
    start_resp = client.post("/api/follow-up/start", json={"symptoms": ["high fever"]})
    state = start_resp.json()["state"]
    q_id = start_resp.json()["question"]["id"]
    
    # We answer 'yes' to whatever it asks, but we also say we have a headache
    ans_resp = client.post(
        "/api/follow-up/answer",
        json={
            "state": state,
            "question_id": q_id,
            "answer": "yes, and I also have headache"
        }
    )
    new_state = ans_resp.json()["state"]
    assert "headache" in new_state["recognized_symptoms"]

def test_followup_duplicate_additional():
    """Test 8 — Duplicate additional symptom"""
    start_resp = client.post("/api/follow-up/start", json={"symptoms": ["headache"]})
    state = start_resp.json()["state"]
    q_id = start_resp.json()["question"]["id"]
    
    ans_resp = client.post(
        "/api/follow-up/answer",
        json={
            "state": state,
            "question_id": q_id,
            "answer": "yes, and I also have headache"
        }
    )
    new_state = ans_resp.json()["state"]
    # headache should only appear once
    assert new_state["recognized_symptoms"].count("headache") == 1

def test_followup_max_limit():
    """Test 9 & 10 — Maximum question limit & completion"""
    start_resp = client.post("/api/follow-up/start", json={"symptoms": ["cough"]})
    data = start_resp.json()
    
    loops = 0
    while not data["complete"] and loops < 10:
        ans_resp = client.post(
            "/api/follow-up/answer",
            json={
                "state": data["state"],
                "question_id": data["question"]["id"],
                "answer": "no"
            }
        )
        data = ans_resp.json()
        loops += 1
        
    assert loops <= 3 # MAX_FOLLOW_UP_QUESTIONS
    assert data["complete"] is True
    assert data["question"] is None
