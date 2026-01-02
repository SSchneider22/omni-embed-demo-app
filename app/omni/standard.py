"""Standard SSO implementation for Omni Embed."""
from typing import Optional
from fastapi import HTTPException, status
from app.config import config
from app.omni.client import omni_client
from app.models import User


async def generate_embed_url_for_user(
    user: User,
    content_path: str
) -> str:
    """
    Generate embed URL for a user using Standard SSO.

    Args:
        user: Authenticated user
        content_path: Path to Omni content

    Returns:
        Embed URL for iframe

    Raises:
        HTTPException: If configuration is invalid or API call fails
    """
    # Validate configuration
    is_valid, error_msg = omni_client.validate_config()
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Omni configuration error: {error_msg}"
        )

    # Validate content path against allowlist
    if content_path not in config.OMNI_CONTENT_PATH_ALLOWLIST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content path not allowed"
        )

    try:
        # Call Omni API to generate embed URL
        result = await omni_client.generate_embed_url(
            content_path=content_path,
            external_id=user.customer_id,
            email=user.email
        )

        # Extract URL from response
        embed_url = result.get("url")
        if not embed_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate embed URL"
            )

        return embed_url

    except Exception as e:
        # Log error but don't expose sensitive details
        # In production, use proper logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate embed URL"
        )
