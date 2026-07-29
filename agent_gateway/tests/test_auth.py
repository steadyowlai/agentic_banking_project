"""
Unit and Integration Tests for Agent Gateway Auth & FastAPI Server
"""

import sys
import os
import json
import pytest
from fastapi.testclient import TestClient

# Add agent_gateway/src to python path
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
GATEWAY_DIR = os.path.dirname(TESTS_DIR)
GATEWAY_SRC = os.path.join(GATEWAY_DIR, "src")
sys.path.insert(0, GATEWAY_SRC)

from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "agent_gateway"}


def test_login_success():
    response = client.post("/auth/login", json={"username": "alice", "password": "hashed_pwd_123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "alice"
    assert data["customer_type"] == "retail"


def test_login_failure():
    response = client.post("/auth/login", json={"username": "alice", "password": "wrong_password"})
    assert response.status_code == 401


def test_protected_route_with_dev_token():
    PROJECT_ROOT = os.path.dirname(GATEWAY_DIR)
    dev_tokens_path = os.path.join(PROJECT_ROOT, "client_side_data", "dev_tokens.json")
    
    with open(dev_tokens_path, "r") as f:
        dev_tokens = json.load(f)

    alice_token = dev_tokens["alice"]["jwt_token"]
    
    headers = {"Authorization": f"Bearer {alice_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    
    user_info = response.json()["user"]
    assert user_info["username"] == "alice"
    assert user_info["customer_type"] == "retail"
    assert user_info["user_id"] == "usr_alice"
