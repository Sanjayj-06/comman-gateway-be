from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.models import User, Command, ApprovalRequest, AuditLog, CommandStatus
from app.schemas import ApprovalRequestResponse, ApprovalAction
from app.dependencies import get_db, get_admin_user
from app.routers.commands import execute_command
import json
from datetime import datetime

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/", response_model=List[ApprovalRequestResponse])
async def list_pending_approvals(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Admin only: Get all pending approval requests
    """
    approvals = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == "pending"
    ).order_by(ApprovalRequest.created_at.desc()).all()
    
    result = []
    for approval in approvals:
        command = db.query(Command).filter(Command.id == approval.command_id).first()
        requester = db.query(User).filter(User.id == approval.requested_by).first()
        
        result.append(ApprovalRequestResponse(
            id=approval.id,
            command_id=approval.command_id,
            command_text=command.command_text if command else "",
            requested_by=approval.requested_by,
            requester_username=requester.username if requester else "Unknown",
            status=approval.status,
            created_at=approval.created_at,
            reviewed_at=approval.reviewed_at,
            approved_by=approval.approved_by,
            approver_username=None
        ))
    
    return result


@router.post("/{approval_id}/review")
async def review_approval(
    approval_id: int,
    action: ApprovalAction,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Admin only: Approve or reject a pending command
    """
    # Get approval request
    approval = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id,
        ApprovalRequest.status == "pending"
    ).first()
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found or already reviewed")
    
    # Get the command
    command = db.query(Command).filter(Command.id == approval.command_id).first()
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    # Get the user who submitted the command
    user = db.query(User).filter(User.id == command.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if action.action == "approve":
        # Approve and execute the command
        approval.status = "approved"
        approval.approved_by = admin.id
        approval.reviewed_at = datetime.utcnow()
        
        try:
            # Execute the command
            execute_command(command, user, db)
            
            # Log approval
            audit_log = AuditLog(
                user_id=admin.id,
                action="COMMAND_APPROVED",
                details=json.dumps({
                    "approval_id": approval.id,
                    "command_id": command.id,
                    "command_text": command.command_text,
                    "requester": user.username
                })
            )
            db.add(audit_log)
            db.commit()
            
            return {
                "message": "Command approved and executed",
                "command_id": command.id,
                "status": command.status
            }
            
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=402, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to execute approved command")
    
    elif action.action == "reject":
        # Reject the command
        approval.status = "rejected"
        approval.approved_by = admin.id
        approval.reviewed_at = datetime.utcnow()
        
        command.status = CommandStatus.REJECTED
        command.result = f"Rejected by admin: {action.reason or 'No reason provided'}"
        
        # Log rejection
        audit_log = AuditLog(
            user_id=admin.id,
            action="COMMAND_REJECTED_BY_ADMIN",
            details=json.dumps({
                "approval_id": approval.id,
                "command_id": command.id,
                "command_text": command.command_text,
                "requester": user.username,
                "reason": action.reason
            })
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "message": "Command rejected",
            "command_id": command.id,
            "status": command.status
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")
