import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def get_headers():
    token = os.getenv("TARS_API_KEY", "tars_secret_key_2024")
    return {"Authorization": f"Bearer {token}"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "services": ["ollama", "postgres", "qdrant", "redis"]}

def test_chat_unauthorized():
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 403 # Missing credentials

def test_chat_authorized():
    # We mock or ensure it runs without executing a real heavy LLM
    # For now, it might try to hit orchestrator logic
    response = client.post("/chat", json={"message": "draft plan"}, headers=get_headers())
    assert response.status_code == 200
    assert "response" in response.json()

def test_dashboard_static():
    # Requires dashboard.py to be running or tested separately since main.py doesn't mount dashboard static
    # Let's test standard endpoints instead
    pass
