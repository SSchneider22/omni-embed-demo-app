"""Omni API client."""
import httpx
from typing import Optional
from app.config import config


class OmniClient:
    """Client for Omni API."""

    def __init__(self):
        self.base_url = config.OMNI_BASE_URL.rstrip("/")
        self.secret = config.OMNI_SECRET

    def validate_config(self) -> tuple[bool, Optional[str]]:
        """Validate Omni configuration."""
        if not self.base_url:
            return False, "OMNI_BASE_URL is not configured"
        if not self.secret:
            return False, "OMNI_SECRET is not configured"
        if not config.OMNI_CONTENT_PATH_ALLOWLIST:
            return False, "OMNI_CONTENT_PATH_ALLOWLIST is not configured"
        return True, None

    async def generate_embed_url(
        self,
        content_path: str,
        external_id: str,
        email: str
    ) -> dict:
        """
        Generate embed URL using Standard SSO (manual generation).

        Calls Omni's /embed/sso/generate-url API.

        Args:
            content_path: Path to Omni content (e.g., /dashboards/abc123)
            external_id: External user ID (customer_id)
            email: User email

        Returns:
            Dictionary with 'url' key containing the embed URL

        Raises:
            httpx.HTTPStatusError: If API call fails
        """
        url = f"{self.base_url}/embed/sso/generate-url"

        payload = {
            "secret": self.secret,
            "contentPath": content_path,
            "externalId": external_id,
            "email": email,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            return response.json()


omni_client = OmniClient()
