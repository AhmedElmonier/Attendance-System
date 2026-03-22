from uuid import UUID
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from cloud.src.db.connection import get_db

from src.services.approval_service import ApprovalService

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])


class ApprovalAction(BaseModel):
    action: str
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


def get_current_user_id(request: Request) -> UUID:
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-ID header")
    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-ID format")


@router.get("/approvals", response_model=List[ApprovalResponse])
async def list_approvals(request: Request, status: Optional[str] = None):
    return []


class MockSession:
    def __init__(self):
        self._data = {}

    def add(self, obj):
        self._data[obj.id] = obj

    def query(self, model):
        class QueryStub:
            def __init__(self, session, model):
                self._session = session
                self._model = model

            def filter(self, *args):
                return self

            def first(self):
                return None

        return QueryStub(self, model)

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def rollback(self):
        pass


@router.post("/approvals/{approval_id}/action", response_model=ApprovalResponse)
async def action_approval(
    approval_id: UUID,
    payload: ApprovalAction,
    request: Request,
):
    checker_id = get_current_user_id(request)
    db_session = MockSession()
    service = ApprovalService(db_session)
    try:
        updated_request = service.review_request(
            request_id=approval_id,
            checker_id=checker_id,
            action=payload.action,
            reason=payload.reason,
        )
        return {
            "id": updated_request.id,
            "entity_type": updated_request.entity_type,
            "status": updated_request.status,
            "maker_id": updated_request.maker_id,
            "checker_id": updated_request.checker_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def search_audit_logs(request: Request, actor_id: Optional[UUID] = None):
    return []
