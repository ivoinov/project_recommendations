import pytest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app  # assuming your FastAPI app is named app and is in the main.py
from routers.schemas import UserSignUp
from database import get_db, SessionLocal

client = TestClient(app)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_login_for_access_token():
    response = client.post(
        "/login",
        data={"username": "user@example.com", "password": "password"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_create_user_signup():
    timestamp = str(time.time())
    email = "testuser" + timestamp + "@example.com"
    username = "testusername" + timestamp

    # First signup should be successful
    response = client.post(
        "/signup",
        json={
            "email": email,
            "password": "testpassword",
            "username": username,
            "full_name": "Test User",
        },
    )
    assert response.status_code == 200

    # Second signup with same email and username should fail
    response = client.post(
        "/signup",
        json={
            "email": email,
            "password": "testpassword",
            "username": username,
            "full_name": "Test User",
        },
    )
    assert response.status_code == 400
