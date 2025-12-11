from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.db.models import User, Rule, Command, AuditLog, ApprovalRequest, CommandStatus, RuleAction
from app.schemas import CommandSubmit, CommandResponse
from app.dependencies import get_db, get_current_user
from app.utils import format_command_result
import re
import json
from datetime import datetime

router = APIRouter(prefix="/commands", tags=["commands"])


def validate_command(command_text: str) -> tuple[bool, str]:
    """
    Validate command for basic syntax and safety.
    Returns (is_valid, error_message)
    """
    # Strip whitespace
    command_text = command_text.strip()
    
    # Check if empty
    if not command_text:
        return False, "Command cannot be empty"
    
    # Check for suspicious patterns that indicate errors
    error_patterns = [
        (r'[\x00-\x08\x0B\x0C\x0E-\x1F]', "Command contains invalid control characters"),
        (r'^[;&|]', "Command cannot start with operators"),
        (r'[;&|]$', "Command cannot end with operators"),
        (r';;+', "Invalid syntax: multiple semicolons"),
        (r'\|\|+', "Invalid syntax: multiple pipes"),
        (r'&&+', "Invalid syntax: multiple ampersands"),
    ]
    
    for pattern, message in error_patterns:
        if re.search(pattern, command_text):
            return False, message
    
    return True, ""


def match_command_against_rules(command_text: str, db: Session) -> tuple[Rule | None, RuleAction | None]:
    """
    Match command against rules ordered by priority.
    Returns (matched_rule, action) or (None, None) if no match.
    """
    rules = db.query(Rule).order_by(Rule.priority.asc(), Rule.id.asc()).all()
    
    for rule in rules:
        try:
            if re.search(rule.pattern, command_text):
                return rule, rule.action
        except re.error:
            # Skip invalid patterns (shouldn't happen due to validation)
            continue
    
    return None, None


def execute_command(command: Command, user: User, db: Session) -> None:
    """
    Execute a command (mocked execution).
    Deducts credits, updates command status, and logs the action.
    All operations must succeed or fail together (transaction).
    """
    try:
        # Check if user has credits
        if user.credits <= 0:
            raise ValueError("Insufficient credits")
        
        # Deduct credits
        user.credits -= 1
        command.credits_deducted = 1
        
        # Mock execution - just log what would happen
        command.status = CommandStatus.EXECUTED
        command.result = format_command_result(command.command_text, "SUCCESS")
        command.executed_at = datetime.utcnow()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            action="COMMAND_EXECUTED",
            details=json.dumps({
                "command_id": command.id,
                "command_text": command.command_text,
                "credits_deducted": 1
            })
        )
        db.add(audit_log)
        
        # Commit all changes together
        db.commit()
        
    except Exception as e:
        # Rollback everything if any step fails
        db.rollback()
        raise e


@router.post("/", response_model=CommandResponse, status_code=201)
async def submit_command(
    command_data: CommandSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a command for execution.
    
    Flow:
    1. Validate command syntax
    2. Check if user has credits > 0
    3. Match against rules (first match wins)
    4. AUTO_ACCEPT → Execute immediately
    5. AUTO_REJECT → Reject and log
    6. REQUIRE_APPROVAL → Set status to pending (bonus feature)
    """
    # Validate command first
    is_valid, error_message = validate_command(command_data.command_text)
    if not is_valid:
        # Create rejected command record
        command = Command(
            command_text=command_data.command_text,
            user_id=current_user.id,
            status=CommandStatus.REJECTED,
            result=f"Invalid command: {error_message}"
        )
        db.add(command)
        db.commit()
        db.refresh(command)
        
        # Log rejection
        audit_log = AuditLog(
            user_id=current_user.id,
            action="COMMAND_REJECTED",
            details=json.dumps({
                "command_id": command.id,
                "command_text": command.command_text,
                "reason": f"VALIDATION_ERROR: {error_message}"
            })
        )
        db.add(audit_log)
        db.commit()
        
        return command
    
    # Check credits
    if current_user.credits <= 0:
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please contact admin to add more credits."
        )
    
    # Match against rules
    matched_rule, action = match_command_against_rules(command_data.command_text, db)
    
    # Create command record
    command = Command(
        command_text=command_data.command_text,
        user_id=current_user.id,
        rule_id=matched_rule.id if matched_rule else None,
        status=CommandStatus.ACCEPTED  # Default status
    )
    
    if action == RuleAction.AUTO_REJECT:
        # Reject the command
        command.status = CommandStatus.REJECTED
        command.result = f"Command rejected by rule: {matched_rule.description or matched_rule.pattern}"
        
        db.add(command)
        db.commit()
        db.refresh(command)
        
        # Log rejection
        audit_log = AuditLog(
            user_id=current_user.id,
            action="COMMAND_REJECTED",
            details=json.dumps({
                "command_id": command.id,
                "command_text": command.command_text,
                "rule_id": matched_rule.id,
                "reason": "AUTO_REJECT"
            })
        )
        db.add(audit_log)
        db.commit()
        
        return command
    
    elif action == RuleAction.AUTO_ACCEPT or matched_rule is None:
        # Auto-accept or no rule matched (default accept)
        db.add(command)
        db.flush()  # Get command ID before execution
        
        try:
            # Execute the command (deducts credits, updates status)
            execute_command(command, current_user, db)
            db.refresh(command)
            return command
            
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=402, detail=str(e))
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database error during command execution")
    
    elif action == RuleAction.REQUIRE_APPROVAL:
        # Bonus feature: require approval
        command.status = CommandStatus.PENDING_APPROVAL
        command.result = "Command requires admin approval"
        
        db.add(command)
        db.flush()  # Get command ID
        
        # Create approval request
        approval_request = ApprovalRequest(
            command_id=command.id,
            requested_by=current_user.id,
            status="pending"
        )
        db.add(approval_request)
        db.commit()
        db.refresh(command)
        
        # Log pending approval
        audit_log = AuditLog(
            user_id=current_user.id,
            action="COMMAND_PENDING_APPROVAL",
            details=json.dumps({
                "command_id": command.id,
                "command_text": command.command_text,
                "rule_id": matched_rule.id
            })
        )
        db.add(audit_log)
        db.commit()
        
        return command
    
    # Should not reach here
    raise HTTPException(status_code=500, detail="Unknown rule action")


@router.get("/", response_model=List[CommandResponse])
async def list_commands(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Get current user's command history"""
    commands = db.query(Command).filter(
        Command.user_id == current_user.id
    ).order_by(Command.submitted_at.desc()).limit(limit).all()
    
    return commands


@router.get("/{command_id}", response_model=CommandResponse)
async def get_command(
    command_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific command by ID"""
    command = db.query(Command).filter(
        Command.id == command_id,
        Command.user_id == current_user.id
    ).first()
    
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return command
