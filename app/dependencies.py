from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User, UserRole
from typing import Optional


def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    x_api_key: str = Header(..., description="API Key for authentication"),
    db: Session = Depends(get_db)
) -> User:
    """
    Authenticate user via API key from header.
    Returns the authenticated user or raises 401.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    
    user = db.query(User).filter(User.api_key == x_api_key).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Requires admin role.
    Returns the admin user or raises 403.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    
    return current_user
