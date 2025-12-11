from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.models import User, Command, AuditLog, CommandStatus
from app.schemas import (
    UserCreate, UserResponse, UserCreateResponse, 
    UserStats, CommandResponse
)
from app.dependencies import get_db, get_current_user, get_admin_user
from app.utils import generate_api_key
import json
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserCreateResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Admin only: Create a new user.
    Returns the user with API key (shown only once).
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Generate API key
    api_key = generate_api_key()
    
    # Create user
    new_user = User(
        username=user_data.username,
        api_key=api_key,
        role=user_data.role,
        credits=100  # Default starting credits
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log action
    audit_log = AuditLog(
        user_id=admin.id,
        action="USER_CREATED",
        details=json.dumps({
            "created_user_id": new_user.id,
            "created_username": new_user.username,
            "role": new_user.role.value
        })
    )
    db.add(audit_log)
    db.commit()
    
    # Return user with API key
    response = UserCreateResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        credits=new_user.credits,
        created_at=new_user.created_at,
        api_key=api_key
    )
    
    return response


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's information"""
    return current_user


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's command statistics"""
    total_commands = db.query(Command).filter(Command.user_id == current_user.id).count()
    executed_commands = db.query(Command).filter(
        Command.user_id == current_user.id,
        Command.status == CommandStatus.EXECUTED
    ).count()
    rejected_commands = db.query(Command).filter(
        Command.user_id == current_user.id,
        Command.status == CommandStatus.REJECTED
    ).count()
    
    return UserStats(
        credits=current_user.credits,
        total_commands=total_commands,
        executed_commands=executed_commands,
        rejected_commands=rejected_commands
    )


@router.get("/me/commands", response_model=List[CommandResponse])
async def get_user_commands(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get current user's command history"""
    commands = db.query(Command).filter(
        Command.user_id == current_user.id
    ).order_by(Command.submitted_at.desc()).limit(limit).all()
    
    return commands


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Admin only: List all users"""
    users = db.query(User).all()
    return users


@router.patch("/{user_id}/credits")
async def update_user_credits(
    user_id: int,
    credits: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Admin only: Update a user's credits"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_credits = user.credits
    user.credits = credits
    db.commit()
    
    # Log action
    audit_log = AuditLog(
        user_id=admin.id,
        action="CREDITS_UPDATED",
        details=json.dumps({
            "target_user_id": user_id,
            "old_credits": old_credits,
            "new_credits": credits
        })
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Credits updated successfully", "new_credits": credits}
