"""Tests for session management."""
import pytest
from fastapi import Response
from app.auth.session import SessionManager
from app.config import config


@pytest.fixture
def session_manager():
    """Create session manager instance."""
    return SessionManager()


def test_create_session(session_manager):
    """Test session creation."""
    response = Response()
    user_id = 123

    session_manager.create_session(response, user_id)

    # Check that cookie was set
    cookies = response.headers.getlist("set-cookie")
    assert len(cookies) > 0

    # Check cookie contains session name
    cookie_str = cookies[0]
    assert config.SESSION_COOKIE_NAME in cookie_str

    # Check HttpOnly flag
    assert "HttpOnly" in cookie_str

    # Check SameSite attribute
    assert "SameSite" in cookie_str


def test_get_user_id_from_valid_session(session_manager, client):
    """Test getting user ID from valid session."""
    # Create a session
    response = Response()
    user_id = 123
    session_manager.create_session(response, user_id)

    # Extract cookie value
    cookies = response.headers.getlist("set-cookie")
    cookie_str = cookies[0]
    # Parse cookie value (format: "session=value; HttpOnly; ...")
    cookie_value = cookie_str.split(";")[0].split("=", 1)[1]

    # Create request with session cookie
    from fastapi import Request
    from starlette.datastructures import Headers

    headers = Headers({"cookie": f"{config.SESSION_COOKIE_NAME}={cookie_value}"})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    # Get user ID from session
    retrieved_user_id = session_manager.get_user_id(request)
    assert retrieved_user_id == user_id


def test_get_user_id_from_invalid_session(session_manager):
    """Test getting user ID from invalid session."""
    from fastapi import Request
    from starlette.datastructures import Headers

    # Request with invalid session token
    headers = Headers({"cookie": f"{config.SESSION_COOKIE_NAME}=invalid-token"})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    retrieved_user_id = session_manager.get_user_id(request)
    assert retrieved_user_id is None


def test_get_user_id_from_missing_session(session_manager):
    """Test getting user ID when session is missing."""
    from fastapi import Request
    from starlette.datastructures import Headers

    # Request without session cookie
    headers = Headers({})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    retrieved_user_id = session_manager.get_user_id(request)
    assert retrieved_user_id is None


def test_delete_session(session_manager):
    """Test session deletion."""
    response = Response()

    session_manager.delete_session(response)

    # Check that cookie deletion was set
    cookies = response.headers.getlist("set-cookie")
    assert len(cookies) > 0

    cookie_str = cookies[0]
    assert config.SESSION_COOKIE_NAME in cookie_str
    # Cookie deletion typically sets max-age=0 or expires in the past
    assert "max-age=0" in cookie_str.lower() or "expires=" in cookie_str.lower()


def test_session_cookie_attributes(session_manager):
    """Test that session cookies have proper security attributes."""
    response = Response()
    user_id = 123

    session_manager.create_session(response, user_id)

    cookies = response.headers.getlist("set-cookie")
    cookie_str = cookies[0]

    # HttpOnly attribute (prevents XSS)
    assert "HttpOnly" in cookie_str

    # SameSite attribute (prevents CSRF)
    assert "SameSite" in cookie_str
    assert "lax" in cookie_str.lower() or "strict" in cookie_str.lower()

    # Max-Age should be set
    assert "Max-Age" in cookie_str or "max-age" in cookie_str
