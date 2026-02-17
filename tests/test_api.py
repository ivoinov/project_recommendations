import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """Test basic health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "recommendation-api"


class TestSignupEndpoint:
    """Tests for user signup functionality."""

    def test_signup_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_signup_duplicate_email(self, client):
        """Test signup fails with duplicate email."""
        user_data = {
            "username": "firstuser",
            "email": "duplicate@example.com",
            "password": "testpass123",
            "full_name": "First User"
        }
        # First signup should succeed
        response = client.post("/signup", json=user_data)
        assert response.status_code == 200

        # Second signup with same email should fail
        user_data["username"] = "seconduser"
        response = client.post("/signup", json=user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_signup_invalid_email(self, client):
        """Test signup fails with invalid email format."""
        response = client.post(
            "/signup",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_signup_password_too_short(self, client):
        """Test signup fails with password shorter than 8 characters."""
        response = client.post(
            "/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422  # Validation error


class TestAuthEndpoint:
    """Tests for user authentication (login) functionality."""

    def test_login_success(self, client):
        """Test successful login after signup."""
        # First create user
        client.post(
            "/signup",
            json={
                "username": "logintest",
                "email": "login@example.com",
                "password": "password123",
                "full_name": "Login Test"
            }
        )

        # Then login (username field is email in this API)
        response = client.post(
            "/auth",
            data={
                "username": "login@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """Test login fails with incorrect password."""
        # First create user
        client.post(
            "/signup",
            json={
                "username": "wrongpasstest",
                "email": "wrongpass@example.com",
                "password": "correctpass123",
                "full_name": "Wrong Pass Test"
            }
        )

        # Try login with wrong password
        response = client.post(
            "/auth",
            data={
                "username": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login fails for non-existent user."""
        response = client.post(
            "/auth",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword123"
            }
        )
        assert response.status_code == 401


class TestRecommendationsEndpoint:
    """Tests for recommendation endpoints."""

    def test_recommendations_requires_auth(self, client):
        """Test that recommendations endpoint requires authentication."""
        response = client.get("/similar-recommendations/SKU123")
        assert response.status_code == 401

    def test_recommendations_with_invalid_token(self, client):
        """Test recommendations endpoint rejects invalid tokens."""
        response = client.get(
            "/similar-recommendations/SKU123",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_upselling_requires_auth(self, client):
        """Test that upselling endpoint requires authentication."""
        response = client.get("/upselling-recommendations/SKU123")
        assert response.status_code == 401
