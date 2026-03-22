import uuid

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.db.session import Base


class RemoteAction(Base):
    __tablename__ = "remote_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kiosk_id = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False)
    signed_payload = Column(Text, nullable=False)
    issued_by = Column(UUID(as_uuid=True), nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="PENDING", nullable=False)
