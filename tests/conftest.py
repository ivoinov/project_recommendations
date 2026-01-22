import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.models.base import Base
from app.models import User, Token, Product, Order, ProductRecommendation
from app.config import db_settings
from main import app
import os

# Test database URL - use environment variable or default to test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test:test@localhost:5433/test_recommendations"
)


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine and tables."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    db = TestingSessionLocal()
    yield db
    db.rollback()
    db.close()


@pytest.fixture
def client(test_db):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[db_settings.get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client, test_db):
    """Create a test client with an authenticated user."""
    # Create a test user
    response = client.post(
        "/signup",
        json={
            "username": "authuser",
            "email": "authuser@example.com",
            "password": "testpass123",
            "full_name": "Auth Test User"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Return client with auth header helper
    client.headers["Authorization"] = f"Bearer {token}"
    return client
