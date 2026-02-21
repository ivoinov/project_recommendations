import importlib.util
import os
import sys
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if os.path.basename(BASE_DIR) == "__pycache__":
    BASE_DIR = os.path.dirname(BASE_DIR)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.models.base import Base
    from app.models import User, Token, Product, Order, ProductRecommendation
    from app.config import db_settings
    from main import app
except ModuleNotFoundError:
    app_init = os.path.join(PROJECT_ROOT, "app", "__init__.py")
    spec = importlib.util.spec_from_file_location(
        "app",
        app_init,
        submodule_search_locations=[os.path.join(PROJECT_ROOT, "app")],
    )
    app_module = importlib.util.module_from_spec(spec)
    sys.modules["app"] = app_module
    if spec and spec.loader:
        spec.loader.exec_module(app_module)
    from app.models.base import Base
    from app.models import User, Token, Product, Order, ProductRecommendation
    from app.config import db_settings
    from main import app

# Test database URL - use environment variable or default to test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://test:test@localhost:5433/test_recommendations"
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
    test_db.execute(text("SET search_path TO public"))
    email = f"authuser-{uuid.uuid4().hex}@example.com"
    username = f"authuser-{uuid.uuid4().hex[:8]}"
    # Create a test user
    response = client.post(
        "/signup",
        json={
            "username": username,
            "email": email,
            "password": "testpass123",
            "full_name": "Auth Test User",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Return client with auth header helper
    client.headers["Authorization"] = f"Bearer {token}"
    return client
