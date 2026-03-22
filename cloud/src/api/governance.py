import os
import jwt
from uuid import UUID
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

from src.models.governance import ApprovalRequest as ApprovalModel, AuditLog
from src.services.approval_service import ApprovalService

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])

_engine = None
_SessionFactory = None


def _get_engine():
    global _engine, _SessionFactory
    if _engine is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            _engine = None
        else:
            _engine = create_engine(db_url, pool_pre_ping=True)
            _SessionFactory = sessionmaker(bind=_engine)
    return _engine, _SessionFactory


def get_db_session() -> Session:
    _, factory = _get_engine()
    if factory is None:
        raise HTTPException(
            status_code=503,
            detail="Database not configured",
        )
    return factory()


def get_current_user_id(request: Request) -> UUID:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authorization must use Bearer scheme"
        )

    token = authorization[7:]
    jwt_secret = os.getenv("JWT_SECRET")
    if not jwt_secret:
        raise HTTPException(
            status_code=500, detail="Server misconfiguration: JWT_SECRET not set"
        )

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"require": ["user_id", "exp"]},
        )
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail=f"Token expired: {e}") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}") from e

    user_id_str = payload.get("user_id")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token missing user_id claim")

    try:
        return UUID(user_id_str)
    except (ValueError, TypeError) as err:
        raise HTTPException(
            status_code=401, detail="Invalid user_id format in token"
        ) from err


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
    actor: UUID
    action: str
    entity: str
    ip: Optional[str] = None
    timestamp: datetime


@router.get("/approvals", response_model=List[ApprovalResponse])
async def list_approvals(request: Request, status: Optional[str] = None):
    tenant_id_str = request.headers.get("X-Tenant-ID")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-ID header")
    try:
        tenant_id = UUID(tenant_id_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid X-Tenant-ID format")

    db = None
    try:
        db = get_db_session()
        query = db.query(ApprovalModel).filter(ApprovalModel.tenant_id == tenant_id)
        if status:
            query = query.filter(ApprovalModel.status == status)
        rows = query.order_by(desc(ApprovalModel.created_at)).all()
        return [
            {
                "id": r.id,
                "entity_type": r.entity_type,
                "status": r.status,
                "maker_id": r.maker_id,
                "checker_id": r.checker_id,
            }
            for r in rows
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve approvals")
    finally:
        if db is not None:
            db.close()


@router.post("/approvals/{approval_id}/action", response_model=ApprovalResponse)
async def action_approval(
    approval_id: UUID,
    payload: ApprovalAction,
    request: Request,
):
    checker_id = get_current_user_id(request)

    tenant_id_str = request.headers.get("X-Tenant-ID")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-ID header")
    try:
        tenant_id = UUID(tenant_id_str)
    except (ValueError, TypeError) as err:
        raise HTTPException(
            status_code=400, detail="Invalid X-Tenant-ID format"
        ) from err

    db = None
    try:
        db = get_db_session()
        service = ApprovalService(db)
        updated_request = service.review_request(
            request_id=approval_id,
            tenant_id=tenant_id,
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
    finally:
        if db is not None:
            db.close()


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def search_audit_logs(request: Request, actor_id: Optional[UUID] = None):
    tenant_id_str = request.headers.get("X-Tenant-ID")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-ID header")
    try:
        tenant_id = UUID(tenant_id_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid X-Tenant-ID format")

    db = None
    try:
        db = get_db_session()
        query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
        if actor_id:
            query = query.filter(AuditLog.actor_id == actor_id)
        rows = query.order_by(desc(AuditLog.timestamp)).limit(500).all()
        return [
            {
                "id": r.id,
                "actor": r.actor_id,
                "action": r.action,
                "entity": r.entity_type,
                "ip": r.ip_address,
                "timestamp": r.timestamp,
            }
            for r in rows
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs")
    finally:
        if db is not None:
            db.close()
