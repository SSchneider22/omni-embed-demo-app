"""CSRF protection."""
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException, status
from app.config import config


class CSRFProtection:
    """CSRF token generation and verification."""

    def __init__(self):
        if not config.SESSION_SECRET:
            raise ValueError("SESSION_SECRET is required")
        self.serializer = URLSafeTimedSerializer(config.SESSION_SECRET, salt="csrf")
        self.token_max_age = 3600  # 1 hour

    def generate_token(self, session_id: str) -> str:
        """Generate a CSRF token."""
        return self.serializer.dumps(session_id)

    def verify_token(self, token: str, session_id: str) -> bool:
        """Verify a CSRF token."""
        try:
            data = self.serializer.loads(token, max_age=self.token_max_age)
            return data == session_id
        except (BadSignature, SignatureExpired):
            return False

    def get_token_from_request(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request (header or form data)."""
        # Check header first
        token = request.headers.get("X-CSRF-Token")
        if token:
            return token

        # Check form data (for non-JSON requests)
        # Note: This is a placeholder - actual form parsing happens in route
        return None


csrf_protection = CSRFProtection()


async def verify_csrf_token(request: Request) -> None:
    """Dependency to verify CSRF token on POST/PUT/PATCH/DELETE requests."""
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        # Get session ID from cookie
        session_cookie = request.cookies.get(config.SESSION_COOKIE_NAME)
        if not session_cookie:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid session"
            )

        # Get CSRF token from request
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            # Try to get from form data
            form = await request.form()
            csrf_token = form.get("csrf_token")

        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )

        # Verify token
        if not csrf_protection.verify_token(csrf_token, session_cookie):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )
