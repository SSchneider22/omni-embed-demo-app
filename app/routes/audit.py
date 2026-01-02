"""Audit logging utilities."""
from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from app.models import AuditLog, User


def log_action(
    db: Session,
    action: str,
    request: Request,
    user: Optional[User] = None,
    resource: Optional[str] = None,
    details: Optional[str] = None
) -> None:
    """
    Log an action to the audit log.

    Args:
        db: Database session
        action: Action performed (e.g., "login", "logout", "view_embed")
        request: FastAPI request
        user: User who performed the action (if authenticated)
        resource: Resource affected (optional)
        details: Additional details (optional)
    """
    log_entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource=resource,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details=details
    )
    db.add(log_entry)
    db.commit()
