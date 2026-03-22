import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, field_validator, model_validator

from src.db.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mobile", tags=["mobile"])


class DeviceRegistration(BaseModel):
    fcm_token: str
    os_type: str
    device_name: str

    @field_validator("os_type")
    @classmethod
    def validate_os(cls, v):
        if v not in ("android", "ios"):
            raise ValueError("os_type must be 'android' or 'ios'")
        return v


class OverrideRequest(BaseModel):
    event_id: str
    action: str
    reason: Optional[str] = None

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        if v not in ("approve", "reject"):
            raise ValueError("action must be 'approve' or 'reject'")
        return v

    @model_validator(mode="after")
    def validate_approve_has_reason(self):
        if self.action == "approve" and not self.reason:
            raise ValueError("reason is mandatory for approve actions")
        return self


class AlertItem(BaseModel):
    event_id: str
    employee_id: str
    employee_name: str
    timestamp: str
    confidence: float
    photo_url: Optional[str] = None


def _get_caller_ids(request: Request):
    tenant_id = getattr(request.state, "tenant_id", None)
    user_id = getattr(request.state, "user_id", None)
    if tenant_id and user_id:
        return tenant_id, user_id
    tenant_str = request.headers.get("X-Tenant-ID", "")
    user_str = request.headers.get("X-User-ID", "")
    try:
        return uuid.UUID(tenant_str), uuid.UUID(user_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Missing X-Tenant-ID or X-User-ID")


@router.post("/register")
async def register_device(request: Request, payload: DeviceRegistration):
    tenant_id, user_id = _get_caller_ids(request)
    try:
        pool = await get_db()
        device_id = await pool.fetchval(
            "INSERT INTO mobile_devices "
            "(id, tenant_id, user_id, fcm_token, os_type, device_name, is_active) "
            "VALUES ($1, $2, $3, $4, $5, $6, true) "
            "ON CONFLICT (fcm_token) DO UPDATE SET "
            "device_name = $6, is_active = true "
            "RETURNING id",
            uuid.uuid4(),
            tenant_id,
            user_id,
            payload.fcm_token,
            payload.os_type,
            payload.device_name,
        )
        logger.info(f"Device registered: {payload.device_name} ({payload.os_type})")
        return {"status": "registered", "device_id": str(device_id)}
    except Exception:
        logger.exception("Device registration failed")
        raise HTTPException(status_code=500, detail="Device registration failed")


@router.get("/alerts", response_model=List[AlertItem])
async def get_unverified_alerts(
    request: Request,
    site_id: Optional[uuid.UUID] = Query(None),
    limit: int = 50,
):
    try:
        pool = await get_db()
        query = (
            "SELECT al.id, al.employee_id, "
            "COALESCE(e.name_en, 'Unknown') as employee_name, "
            "al.timestamp, al.confidence "
            "FROM attendance_logs al "
            "LEFT JOIN employees e ON al.employee_id = e.id "
            "WHERE al.requires_review = true"
        )
        params: list = [limit]
        if site_id:
            query += " AND al.site_id = $2"
            params = [limit, site_id]
        query += " ORDER BY al.timestamp DESC LIMIT $1"
        rows = await pool.fetch(query, *params)
        return [
            AlertItem(
                event_id=str(r["id"]),
                employee_id=str(r["employee_id"]),
                employee_name=r["employee_name"],
                timestamp=r["timestamp"].isoformat() if r["timestamp"] else "",
                confidence=float(r["confidence"]),
            )
            for r in rows
        ]
    except Exception:
        logger.exception("Failed to fetch alerts")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


@router.post("/override")
async def process_override(request: Request, payload: OverrideRequest):
    _, manager_id = _get_caller_ids(request)
    try:
        pool = await get_db()
        new_status = (
            "Present (Manual Override)" if payload.action == "approve" else "Rejected"
        )
        row = await pool.fetchrow(
            "UPDATE attendance_logs SET "
            "requires_review = false, "
            "sync_status = $1, "
            "reviewed_by = $2, "
            "reviewed_at = now(), "
            "reason = $3 "
            "WHERE id = $4 AND requires_review = true "
            "RETURNING id",
            new_status,
            manager_id,
            payload.reason,
            uuid.UUID(payload.event_id),
        )
        if not row:
            raise HTTPException(
                status_code=409,
                detail="Event not found or already reviewed",
            )

        logger.info(
            f"Override processed: {payload.action} for event {payload.event_id} "
            f"reason={payload.reason}"
        )
        return {"status": "processed", "event_id": payload.event_id}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Override processing failed")
        raise HTTPException(status_code=500, detail="Override processing failed")
