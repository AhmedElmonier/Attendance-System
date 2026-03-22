from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])

class ApprovalAction(BaseModel):
    action: str # APPROVED, REJECTED
    reason: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: UUID
    entity_type: str
    status: str
    maker_id: UUID
    checker_id: Optional[UUID]

class AuditLogResponse(BaseModel):
    id: UUID
    actor_id: UUID
    action: str
    entity_type: str
    timestamp: datetime

@router.get("/approvals", response_model=List[ApprovalResponse])
async def list_approvals(request: Request, status: Optional[str] = None):
    # Retrieve pending/history approvals scoped to tenant
    return []

from src.services.approval_service import ApprovalService

@router.post("/approvals/{id}/action", response_model=ApprovalResponse)
async def action_approval(id: UUID, payload: ApprovalAction, request: Request):
    # Dummy DB Session injection simulation
    db_session = MockDB() # In real app, Depends(get_db)
    service = ApprovalService(db_session)
    
    checker_id = "00000000-0000-0000-0000-000000000002"
    try:
        updated_request = service.review_request(
            request_id=id,
            checker_id=UUID(checker_id),
            action=payload.action,
            reason=payload.reason
        )
        return {
            "id": updated_request.id,
            "entity_type": updated_request.entity_type,
            "status": updated_request.status,
            "maker_id": updated_request.maker_id,
            "checker_id": updated_request.checker_id
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def search_audit_logs(request: Request, actor_id: Optional[UUID] = None):
    # Return immutable history
    return []
