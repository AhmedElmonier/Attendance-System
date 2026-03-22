import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.db.connection import get_db
from src.utils.signing import WipeCommandSigner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class WipeRequest(BaseModel):
    kiosk_id: str


class WipeResponse(BaseModel):
    action_id: str
    kiosk_id: str
    status: str
    signed_payload: str


@router.post("/actions/wipe", response_model=WipeResponse)
async def trigger_remote_wipe(request: Request):
    private_key = os.getenv("ED25519_PRIVATE_KEY")
    if not private_key:
        raise HTTPException(
            status_code=500, detail="ED25519_PRIVATE_KEY not configured"
        )

    body = await request.json()
    payload = WipeRequest(**body)

    action_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    nonce = uuid.uuid4().hex

    signer = WipeCommandSigner(private_key)
    signature = signer.sign_wipe_command(payload.kiosk_id, timestamp, nonce)

    signed_payload = json.dumps(
        {
            "action_id": action_id,
            "action": "WIPE_FULL",
            "kiosk_id": payload.kiosk_id,
            "timestamp": timestamp,
            "nonce": nonce,
            "signature": signature,
        },
        sort_keys=True,
    )

    try:
        pool = await get_db()
        await pool.execute(
            "INSERT INTO remote_actions "
            "(id, kiosk_id, action_type, signed_payload, issued_by, status) "
            "VALUES ($1, $2, $3, $4, $5, $6)",
            uuid.UUID(action_id),
            payload.kiosk_id,
            "WIPE_FULL",
            signed_payload,
            uuid.uuid4(),
            "PENDING",
        )
    except Exception:
        logger.exception("Failed to persist wipe action")

    logger.info(f"Wipe action {action_id} created for kiosk {payload.kiosk_id}")

    return WipeResponse(
        action_id=action_id,
        kiosk_id=payload.kiosk_id,
        status="PENDING",
        signed_payload=signed_payload,
    )
