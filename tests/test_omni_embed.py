"""Tests for Omni Embed URL generation."""
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_omni_success():
    """Mock successful Omni API response."""
    async def mock_generate(*args, **kwargs):
        return {"url": "https://test.omni.co/embed/test123?token=abc"}
    return mock_generate


def test_get_embed_url_success(client, test_user, mock_omni_success):
    """Test successful embed URL generation."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Mock Omni API call and allowlist
    with patch("app.omni.client.omni_client.generate_embed_url", new=mock_omni_success), \
         patch("app.config.config.OMNI_CONTENT_PATH_ALLOWLIST", ["/dashboards/test"]):
        # Request embed URL with allowed content path
        response = client.get("/api/embed/url?content_path=/dashboards/test")

        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "https://test.omni.co/embed/test123" in data["url"]


def test_get_embed_url_not_authenticated(client):
    """Test embed URL generation requires authentication."""
    response = client.get("/api/embed/url?content_path=/dashboards/test")
    assert response.status_code == 401


def test_get_embed_url_invalid_content_path(client, test_user, mock_omni_success):
    """Test embed URL generation with content path not in allowlist."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Mock Omni API call
    with patch("app.omni.client.omni_client.generate_embed_url", new=mock_omni_success):
        # Request embed URL with disallowed content path
        response = client.get("/api/embed/url?content_path=/dashboards/forbidden")

        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()


def test_get_embed_url_uses_customer_id(client, test_user):
    """Test that customer_id is used as externalId."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Mock Omni API call and capture arguments
    async def mock_with_capture(*args, **kwargs):
        # Verify customer_id is used as external_id
        assert kwargs.get("external_id") == test_user.customer_id
        assert kwargs.get("email") == test_user.email
        return {"url": "https://test.omni.co/embed/test123?token=abc"}

    with patch("app.omni.client.omni_client.generate_embed_url", new=mock_with_capture), \
         patch("app.config.config.OMNI_CONTENT_PATH_ALLOWLIST", ["/dashboards/test"]):
        response = client.get("/api/embed/url?content_path=/dashboards/test")
        assert response.status_code == 200


def test_get_embed_url_missing_content_path(client, test_user):
    """Test embed URL generation without content_path parameter."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Request without content_path parameter
    response = client.get("/api/embed/url")

    # Should return 422 (validation error)
    assert response.status_code == 422


def test_omni_config_validation_missing_base_url(client, test_user):
    """Test error when OMNI_BASE_URL is not configured."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Mock validate_config to return error
    with patch("app.omni.client.omni_client.validate_config", return_value=(False, "OMNI_BASE_URL is not configured")):
        response = client.get("/api/embed/url?content_path=/dashboards/test")

        assert response.status_code == 500
        assert "configuration error" in response.json()["detail"].lower()


def test_omni_config_validation_missing_secret(client, test_user):
    """Test error when OMNI_SECRET is not configured."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Mock validate_config to return error
    with patch("app.omni.client.omni_client.validate_config", return_value=(False, "OMNI_SECRET is not configured")):
        response = client.get("/api/embed/url?content_path=/dashboards/test")

        assert response.status_code == 500
        assert "configuration error" in response.json()["detail"].lower()


def test_omni_api_failure(client, test_user):
    """Test error handling when Omni API fails."""
    # Login first
    login_response = client.post("/api/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert login_response.status_code == 200

    # Mock Omni API to raise exception
    async def mock_failure(*args, **kwargs):
        raise Exception("Omni API error")

    with patch("app.omni.client.omni_client.generate_embed_url", new=mock_failure), \
         patch("app.config.config.OMNI_CONTENT_PATH_ALLOWLIST", ["/dashboards/test"]):
        response = client.get("/api/embed/url?content_path=/dashboards/test")

        assert response.status_code == 500
        # Should not expose sensitive error details
        assert "Failed to generate embed URL" in response.json()["detail"]
        # Should NOT contain "Omni API error" or other internal details
        assert "Omni API error" not in response.json()["detail"]
