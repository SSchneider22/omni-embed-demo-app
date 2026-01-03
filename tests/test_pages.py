"""Tests for page routes."""


def test_me_page_authenticated(client, test_user):
    """Test /me page displays user information when authenticated."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Access /me page
    response = client.get("/me")
    assert response.status_code == 200

    # Check that user information is displayed
    html_content = response.text
    assert test_user.email in html_content
    assert test_user.customer_id in html_content

    # Check that report links are displayed
    assert "購買分析レポート" in html_content or "レポート" in html_content
    assert "/embed?contentPath=" in html_content


def test_me_page_not_authenticated(client):
    """Test /me page redirects or returns 401 when not authenticated."""
    response = client.get("/me", follow_redirects=False)

    # Should either return 401 or redirect to login
    assert response.status_code in [401, 302, 303, 307, 308]


def test_index_page_not_authenticated(client):
    """Test index page displays correctly when not authenticated."""
    response = client.get("/")
    assert response.status_code == 200

    html_content = response.text
    # Should show login/register links
    assert "ログイン" in html_content or "login" in html_content.lower()
    assert "新規登録" in html_content or "register" in html_content.lower()


def test_index_page_authenticated(client, test_user):
    """Test index page displays user info when authenticated."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Access index page
    response = client.get("/")
    assert response.status_code == 200

    # Should display user information or redirect to /me
    html_content = response.text
    # The index page shows me.html when authenticated
    assert test_user.email in html_content or response.status_code in [302, 303, 307, 308]


def test_register_page_accessible(client):
    """Test /register page is accessible."""
    response = client.get("/register")
    assert response.status_code == 200

    html_content = response.text
    assert "新規登録" in html_content or "register" in html_content.lower()
    assert 'name="email"' in html_content
    assert 'name="password"' in html_content
    assert 'name="customer_id"' in html_content


def test_login_page_accessible(client):
    """Test /login page is accessible."""
    response = client.get("/login")
    assert response.status_code == 200

    html_content = response.text
    assert "ログイン" in html_content or "login" in html_content.lower()
    assert 'name="email"' in html_content
    assert 'name="password"' in html_content
