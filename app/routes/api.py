"""API routes."""
import base64
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db import get_db
from app.models import User
from app.auth.password import hash_password, verify_password
from app.auth.session import session_manager
from app.auth.deps import require_auth
from app.routes.rate_limit import rate_limiter
from app.routes.audit import log_action
from app.omni.standard import generate_embed_url_for_user

router = APIRouter(prefix="/api")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    customer_id: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(
    request: Request,
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Rate limiting
    rate_limiter.check_rate_limit(request, "register")

    # Validate password length
    if len(data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        # Don't reveal that email exists (enumeration protection)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )

    # Check if customer_id already exists
    existing_customer = db.query(User).filter(User.customer_id == data.customer_id).first()
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )

    # Create user
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        customer_id=data.customer_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log action
    log_action(db, "register", request, user=user)

    return {"message": "Registration successful", "user_id": user.id}


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    data: Optional[LoginRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Login endpoint supporting both JSON and Basic Auth.

    Accepts:
    - JSON body with email and password
    - Authorization: Basic header
    """
    # Rate limiting
    rate_limiter.check_rate_limit(request, "login")

    email = None
    password = None

    # Try JSON body first
    if data:
        email = data.email
        password = data.password
    else:
        # Try Basic Auth
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Basic "):
            try:
                credentials = base64.b64decode(auth_header[6:]).decode("utf-8")
                email, password = credentials.split(":", 1)
            except Exception:
                pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

    # Find user
    user = db.query(User).filter(User.email == email).first()

    # Verify password (constant-time to prevent enumeration)
    if not user or not verify_password(password, user.password_hash):
        # Generic error message (enumeration protection)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create session
    session_manager.create_session(response, user.id)

    # Log action
    log_action(db, "login", request, user=user)

    return {"message": "Login successful", "user_id": user.id}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Logout current user."""
    # Log action
    log_action(db, "logout", request, user=user)

    # Delete session
    session_manager.delete_session(response)

    return {"message": "Logout successful"}


@router.get("/me")
async def get_me(
    user: User = Depends(require_auth)
):
    """Get current user info."""
    return {
        "id": user.id,
        "email": user.email,
        "customer_id": user.customer_id,
        "created_at": user.created_at.isoformat()
    }


@router.get("/embed/url")
async def get_embed_url(
    request: Request,
    content_path: str,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Generate Omni embed URL for current user.

    Query params:
        content_path: Omni content path (e.g., /dashboards/abc123)

    Returns:
        {"url": "https://..."}
    """
    # Generate embed URL using Standard SSO
    embed_url = await generate_embed_url_for_user(user, content_path)

    # Log action
    log_action(db, "generate_embed_url", request, user=user, resource=content_path)

    return {"url": embed_url}
