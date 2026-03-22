from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from src.db.session import Base
import uuid

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    entity_type = Column(String, nullable=False) # 'EMPLOYEE', 'BIOMETRIC', 'SITE'
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    change_payload = Column(JSONB, nullable=False)
    maker_id = Column(UUID(as_uuid=True), nullable=False)
    checker_id = Column(UUID(as_uuid=True), nullable=True) # Null until checked
    status = Column(String, default='PENDING', nullable=False) # 'PENDING', 'APPROVED', 'REJECTED'
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    actor_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False) # 'CREATE', 'UPDATE', 'DELETE', 'LOGIN'
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
