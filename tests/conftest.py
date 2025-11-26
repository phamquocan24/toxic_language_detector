"""
Pytest Configuration and Fixtures

Provides common test fixtures and configuration for all tests.
"""

import pytest
import sys
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.models.base import Base
from backend.config.settings import settings


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_toxic_detector.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    
    # Clean up test database file
    if os.path.exists("./test_toxic_detector.db"):
        os.remove("./test_toxic_detector.db")


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Create a new database session for a test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create a test client"""
    from app import app
    
    # Override dependencies if needed
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }


@pytest.fixture(scope="function")
def test_comment_data():
    """Sample comment data for testing"""
    return {
        "text": "This is a test comment",
        "platform": "facebook",
        "platform_id": "test123",
        "source_url": "https://facebook.com/test"
    }


@pytest.fixture(scope="function")
def mock_ml_model(monkeypatch):
    """Mock ML model for testing"""
    class MockModel:
        def predict(self, text):
            # Simple mock prediction
            if "offensive" in text.lower():
                return 1, 0.95, {"clean": 0.05, "offensive": 0.95, "hate": 0.0, "spam": 0.0}
            elif "hate" in text.lower():
                return 2, 0.90, {"clean": 0.05, "offensive": 0.05, "hate": 0.90, "spam": 0.0}
            elif "spam" in text.lower():
                return 3, 0.85, {"clean": 0.10, "offensive": 0.05, "hate": 0.0, "spam": 0.85}
            else:
                return 0, 0.98, {"clean": 0.98, "offensive": 0.01, "hate": 0.0, "spam": 0.01}
    
    return MockModel()


@pytest.fixture(scope="function")
def auth_headers(client, test_user_data):
    """Get auth headers for authenticated requests"""
    # Register user
    client.post("/api/auth/register", json=test_user_data)
    
    # Login to get token
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def redis_mock(monkeypatch):
    """Mock Redis for testing"""
    class MockRedis:
        def __init__(self):
            self.store = {}
            self.expiry = {}
        
        def get(self, key):
            return self.store.get(key)
        
        def set(self, key, value, ex=None):
            self.store[key] = value
            if ex:
                self.expiry[key] = ex
            return True
        
        def delete(self, key):
            self.store.pop(key, None)
            self.expiry.pop(key, None)
            return True
        
        def exists(self, key):
            return key in self.store
        
        def incr(self, key, amount=1):
            current = int(self.store.get(key, 0))
            new_value = current + amount
            self.store[key] = str(new_value)
            return new_value
        
        def expire(self, key, seconds):
            self.expiry[key] = seconds
            return True
        
        def ttl(self, key):
            return self.expiry.get(key, -1)
    
    return MockRedis()


# Pytest configuration
def pytest_configure(config):
    """Pytest configuration"""
    # Set test environment variables
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["REDIS_ENABLED"] = "False"
    os.environ["PROMETHEUS_ENABLED"] = "False"
    os.environ["DEBUG"] = "True"


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)

