from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class RuleAction(str, enum.Enum):
    AUTO_ACCEPT = "AUTO_ACCEPT"
    AUTO_REJECT = "AUTO_REJECT"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class CommandStatus(str, enum.Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXECUTED = "executed"
    PENDING_APPROVAL = "pending_approval"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.MEMBER)
    credits = Column(Integer, nullable=False, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    commands = relationship("Command", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String(500), nullable=False)
    action = Column(Enum(RuleAction), nullable=False)
    description = Column(String(255))
    priority = Column(Integer, default=0)  # Lower number = higher priority
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    commands = relationship("Command", back_populates="matched_rule")


class Command(Base):
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, index=True)
    command_text = Column(Text, nullable=False)
    status = Column(Enum(CommandStatus), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("rules.id"))
    credits_deducted = Column(Integer, default=0)
    result = Column(Text)  # Execution result or rejection reason
    submitted_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime)
    
    user = relationship("User", back_populates="commands")
    matched_rule = relationship("Rule", back_populates="commands")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False) 
    details = Column(Text)  
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    command_id = Column(Integer, ForeignKey("commands.id"), nullable=False, unique=True)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending") 
    approved_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    
    command = relationship("Command", foreign_keys=[command_id])
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])
