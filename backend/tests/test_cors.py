from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cors_preflight_register():
    response = client.options(
        "/api/auth/register",
        headers={
            "Origin": "http://localhost:5176",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5176"
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "authorization" in response.headers.get("access-control-allow-headers", "").lower() or "*" in response.headers.get("access-control-allow-headers", "")

def test_cors_preflight_login():
    response = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://localhost:5176",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5176"
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "authorization" in response.headers.get("access-control-allow-headers", "").lower() or "*" in response.headers.get("access-control-allow-headers", "")

def test_cors_preflight_invalid_origin():
    response = client.options(
        "/api/auth/register",
        headers={
            "Origin": "http://invalid-origin.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type"
        }
    )
    assert response.status_code == 400
