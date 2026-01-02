"""Authentication dependencies."""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.auth.session import session_manager


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from session (optional)."""
    user_id = session_manager.get_user_id(request)
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user


async def require_auth(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Require authentication (raises 401 if not authenticated)."""
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user
