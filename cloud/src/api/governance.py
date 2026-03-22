import os
import logging
import jwt
from uuid import UUID
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.db.connection import get_db, Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])


async def get_current_user_id(request: Request) -> UUID:
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
    actor_name: Optional[str] = None
    action: str
    entity: str
    ip: Optional[str] = None
    timestamp: datetime


def _get_tenant_id(request: Request) -> UUID:
    tenant_id_str = request.headers.get("X-Tenant-ID")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-ID header")
    try:
        return UUID(tenant_id_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid X-Tenant-ID format")


@router.get("/approvals", response_model=List[ApprovalResponse])
async def list_approvals(request: Request, status: Optional[str] = None):
    tenant_id = _get_tenant_id(request)
    try:
        pool = await get_db()
        query = (
            "SELECT id, entity_type, status, maker_id, checker_id "
            "FROM approval_requests WHERE tenant_id = $1"
        )
        params: list = [tenant_id]
        if status:
            query += " AND status = $2"
            params.append(status)
        query += " ORDER BY created_at DESC"
        rows = await pool.fetch(query, *params)
        return [
            {
                "id": r["id"],
                "entity_type": r["entity_type"],
                "status": r["status"],
                "maker_id": r["maker_id"],
                "checker_id": r["checker_id"],
            }
            for r in rows
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve approvals")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve approvals"
        ) from e


@router.post("/approvals/{approval_id}/action", response_model=ApprovalResponse)
async def action_approval(
    approval_id: UUID,
    payload: ApprovalAction,
    request: Request,
):
    checker_id = await get_current_user_id(request)
    tenant_id = _get_tenant_id(request)

    try:
        pool = await get_db()
        row = await pool.fetchrow(
            "SELECT id, tenant_id, maker_id, entity_type, entity_id, "
            "change_payload, status, checker_id, reason "
            "FROM approval_requests "
            "WHERE id = $1 AND tenant_id = $2",
            approval_id,
            tenant_id,
        )
        if not row:
            raise HTTPException(status_code=404, detail="Approval request not found")

        if str(row["maker_id"]) == str(checker_id):
            raise HTTPException(status_code=403, detail="Self-approval is forbidden")

        if row["status"] != "PENDING":
            raise HTTPException(
                status_code=409,
                detail=f"Cannot review request. Currently in state: {row['status']}",
            )

        if payload.action not in ["APPROVED", "REJECTED"]:
            raise HTTPException(status_code=400, detail="Invalid action")

        if payload.action == "APPROVED":
            from src.services.approval_service import apply_changes

            try:
                apply_changes(
                    row["entity_type"],
                    row["entity_id"],
                    row["change_payload"],
                )
            except NotImplementedError as e:
                raise HTTPException(status_code=501, detail=str(e)) from e

        updated = await pool.fetchrow(
            "UPDATE approval_requests "
            "SET status = $1, checker_id = $2, reason = $3 "
            "WHERE id = $4 "
            "RETURNING id, entity_type, status, maker_id, checker_id",
            payload.action,
            checker_id,
            payload.reason,
            approval_id,
        )
        return {
            "id": updated["id"],
            "entity_type": updated["entity_type"],
            "status": updated["status"],
            "maker_id": updated["maker_id"],
            "checker_id": updated["checker_id"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to process approval action")
        raise HTTPException(
            status_code=500, detail="Failed to process approval action"
        ) from e


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def search_audit_logs(request: Request, actor_id: Optional[UUID] = None):
    tenant_id = _get_tenant_id(request)
    try:
        pool = await get_db()
        query = (
            "SELECT al.id, al.actor_id, al.action, al.entity_type, "
            "al.ip_address, al.timestamp "
            "FROM audit_logs al "
            "WHERE al.tenant_id = $1"
        )
        params: list = [tenant_id]
        if actor_id:
            query += " AND al.actor_id = $2"
            params.append(actor_id)
        query += " ORDER BY al.timestamp DESC LIMIT 500"
        rows = await pool.fetch(query, *params)
        return [
            {
                "id": r["id"],
                "actor": r["actor_id"],
                "actor_name": None,  # TODO: JOIN users table when schema is ready
                "action": r["action"],
                "entity": r["entity_type"],
                "ip": r["ip_address"],
                "timestamp": r["timestamp"],
            }
            for r in rows
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve audit logs")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve audit logs"
        ) from e
