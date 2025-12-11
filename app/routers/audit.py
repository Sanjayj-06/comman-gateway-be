from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.models import User, AuditLog
from app.schemas import AuditLogResponse
from app.dependencies import get_db, get_admin_user

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
    limit: int = 100
):
    """
    Admin only: Get audit logs.
    Returns recent audit entries with username information.
    """
    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).limit(limit).all()
    
    # Enrich with username
    result = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp,
            "username": user.username if user else "Unknown"
        }
        result.append(AuditLogResponse(**log_dict))
    
    return result


@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
async def get_user_audit_logs(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
    limit: int = 100
):
    """
    Admin only: Get audit logs for a specific user.
    """
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(
        AuditLog.timestamp.desc()
    ).limit(limit).all()
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Enrich with username
    result = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp,
            "username": user.username
        }
        result.append(AuditLogResponse(**log_dict))
    
    return result
