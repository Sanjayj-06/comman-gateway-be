from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from app.db.models import UserRole, RuleAction, CommandStatus
import re



class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.MEMBER


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    credits: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserCreateResponse(UserResponse):
    api_key: str 



class RuleBase(BaseModel):
    pattern: str = Field(..., min_length=1, max_length=500)
    action: RuleAction
    description: Optional[str] = Field(None, max_length=255)
    priority: int = Field(default=0)
    
    @validator('pattern')
    def validate_regex(cls, v):
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {str(e)}")
        return v


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    pattern: Optional[str] = Field(None, min_length=1, max_length=500)
    action: Optional[RuleAction] = None
    description: Optional[str] = Field(None, max_length=255)
    priority: Optional[int] = None
    
    @validator('pattern')
    def validate_regex(cls, v):
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {str(e)}")
        return v


class RuleResponse(RuleBase):
    id: int
    created_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True



class CommandSubmit(BaseModel):
    command_text: str = Field(..., min_length=1)


class CommandResponse(BaseModel):
    id: int
    command_text: str
    status: CommandStatus
    credits_deducted: int
    result: Optional[str]
    submitted_at: datetime
    executed_at: Optional[datetime]
    rule_id: Optional[int]
    
    class Config:
        from_attributes = True



class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    details: Optional[str]
    timestamp: datetime
    username: Optional[str] = None
    
    class Config:
        from_attributes = True



class UserStats(BaseModel):
    credits: int
    total_commands: int
    executed_commands: int
    rejected_commands: int



class ApprovalRequestResponse(BaseModel):
    id: int
    command_id: int
    command_text: str
    requested_by: int
    requester_username: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]
    approved_by: Optional[int]
    approver_username: Optional[str]
    
    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    action: str  # "approve" or "reject"
    reason: Optional[str] = None
