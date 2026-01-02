"""Integration tests for authentication flow."""


def test_register_user(client):
    """Test user registration."""
    response = client.post("/api/register", json={
        "email": "newuser@example.com",
        "password": "newpassword123",
        "customer_id": "new-customer-001"
    })

    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["message"] == "Registration successful"


def test_register_user_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = client.post("/api/register", json={
        "email": test_user.email,
        "password": "somepassword123",
        "customer_id": "another-customer-002"
    })

    # Should fail with 400 but not reveal that email exists (enumeration protection)
    assert response.status_code == 400
    assert response.json()["detail"] == "Registration failed"


def test_register_user_weak_password(client):
    """Test registration with weak password."""
    response = client.post("/api/register", json={
        "email": "weak@example.com",
        "password": "short",
        "customer_id": "weak-customer-003"
    })

    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "user_id" in data

    # Check session cookie is set
    assert "session" in response.cookies


def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post("/api/login", json={
        "email": "nonexistent@example.com",
        "password": "somepassword123"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_current_user_authenticated(client, test_user):
    """Test getting current user info when authenticated."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Get current user info
    response = client.get("/api/me")
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == test_user.email
    assert data["customer_id"] == test_user.customer_id
    assert "id" in data
    assert "created_at" in data


def test_get_current_user_not_authenticated(client):
    """Test getting current user info when not authenticated."""
    response = client.get("/api/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_logout(client, test_user):
    """Test logout."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Logout
    logout_response = client.post("/api/logout")
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logout successful"

    # Verify session is cleared - subsequent request should fail
    me_response = client.get("/api/me")
    assert me_response.status_code == 401


def test_session_persistence(client, test_user):
    """Test that session persists across requests."""
    # Login
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Multiple requests should work with same session
    for _ in range(3):
        response = client.get("/api/me")
        assert response.status_code == 200
        assert response.json()["email"] == test_user.email


def test_session_cookie_attributes(client, test_user):
    """Test that session cookies have proper security attributes."""
    response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })

    assert response.status_code == 200

    # Check cookie attributes through response headers
    set_cookie_header = response.headers.get("set-cookie", "")

    # HttpOnly prevents XSS
    assert "HttpOnly" in set_cookie_header

    # SameSite prevents CSRF
    assert "SameSite" in set_cookie_header
