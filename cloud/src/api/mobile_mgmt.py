import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator

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

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v, info):
        action = info.data.get("action")
        if action == "approve" and not v:
            raise ValueError("reason is mandatory for approve actions")
        return v


class AlertItem(BaseModel):
    event_id: str
    employee_id: str
    employee_name: str
    timestamp: str
    confidence: float
    photo_url: Optional[str] = None


@router.post("/register")
async def register_device(request: Request):
    body = await request.json()
    payload = DeviceRegistration(**body)

    try:
        pool = await get_db()
        device_id = uuid.uuid4()
        await pool.execute(
            "INSERT INTO mobile_devices "
            "(id, tenant_id, user_id, fcm_token, os_type, device_name, is_active) "
            "VALUES ($1, $2, $3, $4, $5, $6, true) "
            "ON CONFLICT (fcm_token) DO UPDATE SET "
            "device_name = $6, is_active = true",
            device_id,
            uuid.uuid4(),
            uuid.uuid4(),
            payload.fcm_token,
            payload.os_type,
            payload.device_name,
        )
        logger.info(f"Device registered: {payload.device_name} ({payload.os_type})")
        return {"status": "registered", "device_id": str(device_id)}
    except Exception as e:
        logger.exception("Device registration failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/alerts", response_model=List[AlertItem])
async def get_unverified_alerts(
    request: Request, site_id: Optional[str] = None, limit: int = 50
):
    try:
        pool = await get_db()
        query = (
            "SELECT al.id, al.employee_id, "
            "COALESCE(e.name_en, 'Unknown') as employee_name, "
            "al.timestamp, al.confidence "
            "FROM attendance_logs al "
            "LEFT JOIN employees e ON al.employee_id = e.id "
            "WHERE al.requires_review = true "
            "ORDER BY al.timestamp DESC LIMIT $1"
        )
        rows = await pool.fetch(query, limit)
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
    except Exception as e:
        logger.exception("Failed to fetch alerts")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/override")
async def process_override(request: Request):
    body = await request.json()
    payload = OverrideRequest(**body)

    try:
        pool = await get_db()
        row = await pool.fetchrow(
            "SELECT id, requires_review FROM attendance_logs WHERE id = $1",
            uuid.UUID(payload.event_id),
        )
        if not row:
            raise HTTPException(status_code=404, detail="Event not found")
        if not row["requires_review"]:
            raise HTTPException(status_code=409, detail="Event already reviewed")

        reviewed_by = uuid.uuid4()
        new_status = (
            "Present (Manual Override)" if payload.action == "approve" else "Rejected"
        )
        await pool.execute(
            "UPDATE attendance_logs SET "
            "requires_review = false, "
            "sync_status = $1 "
            "WHERE id = $2",
            new_status,
            uuid.UUID(payload.event_id),
        )

        logger.info(
            f"Override processed: {payload.action} for event {payload.event_id} "
            f"reason={payload.reason}"
        )
        return {"status": "processed", "event_id": payload.event_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Override processing failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
