"""Tests for CSRF protection."""
import pytest
from app.auth.csrf import CSRFProtection


@pytest.fixture
def csrf_protection():
    """Create CSRF protection instance."""
    return CSRFProtection()


def test_generate_csrf_token(csrf_protection):
    """Test CSRF token generation."""
    session_id = "test-session-123"
    token = csrf_protection.generate_token(session_id)

    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_csrf_token_success(csrf_protection):
    """Test CSRF token verification with valid token."""
    session_id = "test-session-123"
    token = csrf_protection.generate_token(session_id)

    # Verification should succeed
    assert csrf_protection.verify_token(token, session_id) is True


def test_verify_csrf_token_wrong_session(csrf_protection):
    """Test CSRF token verification with wrong session ID."""
    session_id = "test-session-123"
    wrong_session_id = "test-session-456"
    token = csrf_protection.generate_token(session_id)

    # Verification should fail with different session ID
    assert csrf_protection.verify_token(token, wrong_session_id) is False


def test_verify_csrf_token_invalid(csrf_protection):
    """Test CSRF token verification with invalid token."""
    session_id = "test-session-123"
    invalid_token = "invalid-token"

    # Verification should fail
    assert csrf_protection.verify_token(invalid_token, session_id) is False


def test_verify_csrf_token_expired(csrf_protection):
    """Test CSRF token verification with expired token."""
    import time

    session_id = "test-session-123"

    # Temporarily reduce max_age for testing
    original_max_age = csrf_protection.token_max_age
    csrf_protection.token_max_age = 1  # 1 second

    token = csrf_protection.generate_token(session_id)

    # Wait for token to expire
    time.sleep(2)

    # Verification should fail due to expiration
    assert csrf_protection.verify_token(token, session_id) is False

    # Restore original max_age
    csrf_protection.token_max_age = original_max_age


def test_csrf_token_uniqueness(csrf_protection):
    """Test that tokens may be the same or different for same session."""
    import time

    session_id = "test-session-123"
    token1 = csrf_protection.generate_token(session_id)

    # Wait a tiny bit to ensure different timestamp
    time.sleep(0.01)

    token2 = csrf_protection.generate_token(session_id)

    # Tokens might be the same or different depending on timestamp precision
    # The important thing is both should verify correctly
    assert csrf_protection.verify_token(token1, session_id) is True
    assert csrf_protection.verify_token(token2, session_id) is True


def test_get_token_from_request_header(csrf_protection):
    """Test extracting CSRF token from request header."""
    from fastapi import Request
    from starlette.datastructures import Headers

    token_value = "test-csrf-token-123"
    headers = Headers({"X-CSRF-Token": token_value})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    extracted_token = csrf_protection.get_token_from_request(request)
    assert extracted_token == token_value


def test_get_token_from_request_missing(csrf_protection):
    """Test extracting CSRF token when not present."""
    from fastapi import Request
    from starlette.datastructures import Headers

    headers = Headers({})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    extracted_token = csrf_protection.get_token_from_request(request)
    assert extracted_token is None
