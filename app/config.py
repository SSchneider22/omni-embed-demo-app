"""Application configuration."""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Application
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = APP_ENV == "development"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

    # Session
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "")
    SESSION_COOKIE_NAME: str = "session"
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_COOKIE_SECURE: bool = APP_ENV == "production"
    SESSION_MAX_AGE: int = 86400  # 24 hours

    # Omni Embed - Standard SSO (manual generation)
    OMNI_BASE_URL: str = os.getenv("OMNI_BASE_URL", "")
    OMNI_SECRET: str = os.getenv("OMNI_SECRET", "")
    OMNI_CONTENT_PATH_ALLOWLIST: List[str] = [
        path.strip()
        for path in os.getenv("OMNI_CONTENT_PATH_ALLOWLIST", "").split(",")
        if path.strip()
    ]

    # Rate Limiting (simple in-memory)
    RATE_LIMIT_LOGIN: int = 5  # attempts per window
    RATE_LIMIT_WINDOW: int = 300  # 5 minutes in seconds

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        errors = []

        if not cls.SESSION_SECRET or len(cls.SESSION_SECRET) < 32:
            errors.append("SESSION_SECRET must be at least 32 characters")

        if not cls.OMNI_BASE_URL:
            errors.append("OMNI_BASE_URL is required")

        if not cls.OMNI_SECRET:
            errors.append("OMNI_SECRET is required")

        if not cls.OMNI_CONTENT_PATH_ALLOWLIST:
            errors.append("OMNI_CONTENT_PATH_ALLOWLIST is required")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


config = Config()
