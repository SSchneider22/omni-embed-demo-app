"""Pytest configuration and fixtures."""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db import Base, get_db
from app.main import app
from app.models import User
from app.auth.password import hash_password


# Use in-memory SQLite for tests with StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create a test database."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Use StaticPool for in-memory SQLite in tests
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Reset rate limiter before each test
    from app.routes.rate_limit import rate_limiter
    rate_limiter.attempts.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        customer_id="test-customer-001"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(autouse=True)
def set_test_env():
    """Set test environment variables."""
    os.environ["SESSION_SECRET"] = "test-secret-key-min-32-chars-for-testing-purposes"
    os.environ["APP_ENV"] = "testing"
    os.environ["OMNI_BASE_URL"] = "https://test.omni.co"
    os.environ["OMNI_SECRET"] = "test-omni-secret"
    os.environ["OMNI_CONTENT_PATH_ALLOWLIST"] = "/dashboards/test"
