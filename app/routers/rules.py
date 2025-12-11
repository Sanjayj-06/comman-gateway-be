from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.models import User, Rule, AuditLog
from app.schemas import RuleCreate, RuleUpdate, RuleResponse
from app.dependencies import get_db, get_current_user, get_admin_user
import json

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/", response_model=RuleResponse, status_code=201)
async def create_rule(
    rule_data: RuleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Admin only: Create a new rule.
    Pattern must be a valid regex.
    """
    # Create rule
    new_rule = Rule(
        pattern=rule_data.pattern,
        action=rule_data.action,
        description=rule_data.description,
        priority=rule_data.priority,
        created_by=admin.id
    )
    
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    
    # Log action
    audit_log = AuditLog(
        user_id=admin.id,
        action="RULE_CREATED",
        details=json.dumps({
            "rule_id": new_rule.id,
            "pattern": new_rule.pattern,
            "action": new_rule.action.value
        })
    )
    db.add(audit_log)
    db.commit()
    
    return new_rule


@router.get("/", response_model=List[RuleResponse])
async def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all rules ordered by priority"""
    rules = db.query(Rule).order_by(Rule.priority.asc(), Rule.id.asc()).all()
    return rules


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific rule by ID"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Admin only: Update an existing rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update fields if provided
    if rule_data.pattern is not None:
        rule.pattern = rule_data.pattern
    if rule_data.action is not None:
        rule.action = rule_data.action
    if rule_data.description is not None:
        rule.description = rule_data.description
    if rule_data.priority is not None:
        rule.priority = rule_data.priority
    
    db.commit()
    db.refresh(rule)
    
    # Log action
    audit_log = AuditLog(
        user_id=admin.id,
        action="RULE_UPDATED",
        details=json.dumps({
            "rule_id": rule.id,
            "pattern": rule.pattern,
            "action": rule.action.value
        })
    )
    db.add(audit_log)
    db.commit()
    
    return rule


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Admin only: Delete a rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Log action before deletion
    audit_log = AuditLog(
        user_id=admin.id,
        action="RULE_DELETED",
        details=json.dumps({
            "rule_id": rule.id,
            "pattern": rule.pattern,
            "action": rule.action.value
        })
    )
    db.add(audit_log)
    
    db.delete(rule)
    db.commit()
    
    return {"message": "Rule deleted successfully"}
