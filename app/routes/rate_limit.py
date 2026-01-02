"""Simple in-memory rate limiting."""
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from app.config import config


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        # Structure: {(ip, endpoint): [(timestamp, count)]}
        self.attempts: Dict[Tuple[str, str], list] = defaultdict(list)

    def check_rate_limit(
        self,
        request: Request,
        endpoint: str,
        max_attempts: int = None,
        window_seconds: int = None
    ) -> None:
        """
        Check rate limit for a request.

        Args:
            request: FastAPI request
            endpoint: Endpoint identifier
            max_attempts: Maximum attempts allowed (default from config)
            window_seconds: Time window in seconds (default from config)

        Raises:
            HTTPException: If rate limit exceeded
        """
        max_attempts = max_attempts or config.RATE_LIMIT_LOGIN
        window_seconds = window_seconds or config.RATE_LIMIT_WINDOW

        ip = request.client.host if request.client else "unknown"
        key = (ip, endpoint)

        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)

        # Clean up old attempts
        self.attempts[key] = [
            ts for ts in self.attempts[key]
            if ts > cutoff
        ]

        # Check if rate limit exceeded
        if len(self.attempts[key]) >= max_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )

        # Record this attempt
        self.attempts[key].append(now)


rate_limiter = RateLimiter()
