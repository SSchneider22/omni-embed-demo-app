"""Tests for authentication dependencies."""
import pytest
from fastapi import HTTPException
from app.auth.deps import get_current_user, require_auth


@pytest.mark.asyncio
async def test_get_current_user_authenticated(client, test_user, test_db):
    """Test get_current_user with authenticated user."""
    # Login to get session cookie
    response = client.post("/api/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200

    # Extract session cookie
    cookies = response.cookies

    # Create request with session cookie
    from fastapi import Request
    from starlette.datastructures import Headers

    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    headers = Headers({"cookie": cookie_str})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    # Get current user
    user = await get_current_user(request, test_db)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_not_authenticated(test_db):
    """Test get_current_user without authentication."""
    from fastapi import Request
    from starlette.datastructures import Headers

    # Request without session cookie
    headers = Headers({})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    user = await get_current_user(request, test_db)
    assert user is None


@pytest.mark.asyncio
async def test_require_auth_authenticated(client, test_user, test_db):
    """Test require_auth with authenticated user."""
    # Login to get session cookie
    response = client.post("/api/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200

    # Extract session cookie
    cookies = response.cookies

    # Create request with session cookie
    from fastapi import Request
    from starlette.datastructures import Headers

    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    headers = Headers({"cookie": cookie_str})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    # Require auth should succeed
    user = await require_auth(request, test_db)
    assert user is not None
    assert user.id == test_user.id


@pytest.mark.asyncio
async def test_require_auth_not_authenticated(test_db):
    """Test require_auth without authentication."""
    from fastapi import Request
    from starlette.datastructures import Headers

    # Request without session cookie
    headers = Headers({})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    # Require auth should raise 401
    with pytest.raises(HTTPException) as exc_info:
        await require_auth(request, test_db)

    assert exc_info.value.status_code == 401
    assert "Authentication required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_require_auth_invalid_session(test_db):
    """Test require_auth with invalid session."""
    from fastapi import Request
    from starlette.datastructures import Headers
    from app.config import config

    # Request with invalid session token
    headers = Headers({"cookie": f"{config.SESSION_COOKIE_NAME}=invalid-token"})
    scope = {"type": "http", "headers": headers.raw}
    request = Request(scope)

    # Require auth should raise 401
    with pytest.raises(HTTPException) as exc_info:
        await require_auth(request, test_db)

    assert exc_info.value.status_code == 401
