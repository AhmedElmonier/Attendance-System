import base64
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List

import asyncpg
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from cloud.src.core.security import verify_event_integrity, verify_ntp_drift
from cloud.src.db.connection import Database, get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttendanceEvent(BaseModel):
    event_id: str
    employee_id: str
    timestamp: str
    confidence: float
    integrity_hash: str
    zone: str = "green"
    requires_review: bool = False


class SyncRequest(BaseModel):
    batch_id: str
    kiosk_timestamp: str
    events: List[AttendanceEvent]


class SyncResponse(BaseModel):
    status: str
    synced_count: int
    server_time: str
    rejected: Optional[List[str]] = None


class DeviceProvisionRequest(BaseModel):
    device_name: str
    tenant_id: str
    certificate_cn: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.connect()
    logger.info("Starting Attendance API")
    yield
    await Database.disconnect()
    logger.info("Shutting down Attendance API")


ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") or [
    "http://localhost:3000"
]

app = FastAPI(
    title="Attendance System API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Liveness probe: returns 200 if the service is running.
    For readiness (DB connectivity), use /ready.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ready")
async def readiness_check():
    """
    Readiness probe: returns 503 if database is unreachable.
    """
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": "disconnected",
                "reason": "Database connection failed",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


def extract_tenant_from_auth(authorization: Optional[str]) -> Optional[str]:
    """
    Extract tenant_id from a Bearer token.
    Token format: base64-encoded JSON with 'tenant_id' field.
    Returns None if token is invalid or missing.
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        logger.warning("Authorization header does not use Bearer scheme")
        return None

    token = authorization[7:]

    try:
        decoded = base64.b64decode(token + "==").decode("utf-8")
        payload = json.loads(decoded)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.warning(f"Failed to decode token: {e}")
        return None

    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        logger.warning("Token payload missing 'tenant_id' field")
        return None

    return tenant_id


@app.post("/api/v1/sync/attendance", response_model=SyncResponse)
async def sync_attendance(
    request: SyncRequest,
    x_device_id: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    pool: asyncpg.Pool = Depends(get_db),
):
    """
    Sync attendance events from edge devices.
    Requires valid Bearer token with tenant_id in payload.
    """
    logger.info(
        f"Received sync batch: {request.batch_id} ({len(request.events)} events)"
    )

    if not authorization:
        logger.warning("Sync request missing authorization header")
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header. Bearer token required.",
        )

    tenant_id = extract_tenant_from_auth(authorization)
    if not tenant_id:
        logger.warning("Invalid or expired authorization token")
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization token. Provide a valid Bearer token.",
        )

    logger.info(f"Authenticated tenant: {tenant_id}")

    drift_ok, drift_msg = verify_ntp_drift(request.kiosk_timestamp)
    if not drift_ok:
        logger.warning(f"NTP drift check failed: {drift_msg}")
        raise HTTPException(
            status_code=400,
            detail=f"NTP drift detected: {drift_msg}",
        )

    rejected: List[str] = []
    synced_count = 0
    rejected_count = 0

    async with pool.acquire() as conn:
        for event in request.events:
            event_dict = event.model_dump()

            if not verify_event_integrity(event_dict):
                rejected.append(event.event_id)
                rejected_count += 1
                logger.warning(
                    f"Integrity check failed for event {event.event_id} "
                    f"at {event.timestamp}"
                )
                continue

            try:
                await conn.execute(
                    """
                    INSERT INTO attendance_events
                    (id, tenant_id, employee_id, event_timestamp, confidence_score,
                     zone, requires_review, event_type, integrity_hash, client_timestamp, synced_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
                    ON CONFLICT (id) DO NOTHING
                    """,
                    event.event_id,
                    tenant_id,
                    event.employee_id,
                    event.timestamp,
                    event.confidence,
                    event.zone,
                    event.requires_review,
                    "clock_in",
                    event.integrity_hash,
                    request.kiosk_timestamp,
                )
                synced_count += 1
                logger.debug(f"Inserted event {event.event_id}")

            except Exception as e:
                rejected.append(event.event_id)
                rejected_count += 1
                logger.error(f"Database error for event {event.event_id}: {e}")

    response = SyncResponse(
        status="success" if synced_count > 0 else "no_events",
        synced_count=synced_count,
        server_time=datetime.utcnow().isoformat() + "Z",
        rejected=rejected if rejected else None,
    )

    logger.info(
        f"Sync complete for tenant {tenant_id}: "
        f"{synced_count} synced, {rejected_count} rejected"
    )
    return response


@app.post("/api/v1/devices/provision")
async def provision_device(request: DeviceProvisionRequest):
    """
    Provision a new edge device for a tenant.
    Returns placeholder values - implement secure certificate issuance in production.
    """
    logger.info(f"Device provision request: {request.device_name}")
    return {
        "device_id": "placeholder-device-id",
        "status": "provisioned",
        "certificate": "placeholder-cert",
    }


@app.get("/api/v1/attendance/events")
async def get_attendance_events(
    tenant_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    employee_id: Optional[str] = None,
    limit: int = 100,
    pool: asyncpg.Pool = Depends(get_db),
):
    """
    Retrieve attendance events for a tenant with optional filters.
    """
    logger.info(f"Fetching attendance events for tenant {tenant_id}")

    query = """
        SELECT id, employee_id, event_timestamp, confidence_score, event_type
        FROM attendance_events
        WHERE tenant_id = $1
    """
    params: List = [tenant_id]

    if start_date:
        params.append(start_date)
        query += f" AND event_timestamp >= ${len(params)}"

    if end_date:
        params.append(end_date)
        query += f" AND event_timestamp <= ${len(params)}"

    if employee_id:
        params.append(employee_id)
        query += f" AND employee_id = ${len(params)}"

    query += f" ORDER BY event_timestamp DESC LIMIT ${len(params) + 1}"
    params.append(limit)

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    events = [
        {
            "id": str(row["id"]),
            "employee_id": str(row["employee_id"]),
            "timestamp": row["event_timestamp"].isoformat(),
            "confidence": row["confidence_score"],
            "event_type": row["event_type"],
        }
        for row in rows
    ]

    return {"events": events, "count": len(events), "has_more": len(rows) == limit}
