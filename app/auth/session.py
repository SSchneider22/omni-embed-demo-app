"""Session management using signed cookies."""
from datetime import datetime, timedelta
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, Response
from app.config import config


class SessionManager:
    """Manage user sessions with signed cookies."""

    def __init__(self):
        if not config.SESSION_SECRET:
            raise ValueError("SESSION_SECRET is required")
        self.serializer = URLSafeTimedSerializer(config.SESSION_SECRET)
        self.cookie_name = config.SESSION_COOKIE_NAME
        self.max_age = config.SESSION_MAX_AGE

    def create_session(self, response: Response, user_id: int) -> None:
        """Create a new session for a user."""
        session_data = {"user_id": user_id, "created_at": datetime.utcnow().isoformat()}
        token = self.serializer.dumps(session_data)

        response.set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=self.max_age,
            httponly=config.SESSION_COOKIE_HTTPONLY,
            secure=config.SESSION_COOKIE_SECURE,
            samesite=config.SESSION_COOKIE_SAMESITE,
        )

    def get_user_id(self, request: Request) -> Optional[int]:
        """Get user ID from session cookie."""
        token = request.cookies.get(self.cookie_name)
        if not token:
            return None

        try:
            session_data = self.serializer.loads(token, max_age=self.max_age)
            return session_data.get("user_id")
        except (BadSignature, SignatureExpired):
            return None

    def delete_session(self, response: Response) -> None:
        """Delete a session."""
        response.delete_cookie(key=self.cookie_name)


session_manager = SessionManager()
