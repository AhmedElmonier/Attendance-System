import os
import json
import uuid
import logging
from datetime import datetime, timezone

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


def _get_admin_id(request: Request) -> uuid.UUID:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Missing authenticated user ID")
    try:
        return uuid.UUID(str(user_id))
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=401, detail="Invalid authenticated user ID"
        ) from e


@router.post("/actions/wipe", response_model=WipeResponse)
async def trigger_remote_wipe(request: Request, payload: WipeRequest):
    private_key = os.getenv("ED25519_PRIVATE_KEY")
    if not private_key:
        raise HTTPException(
            status_code=500, detail="ED25519_PRIVATE_KEY not configured"
        )

    admin_id = _get_admin_id(request)

    action_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    nonce = uuid.uuid4().hex

    signer = WipeCommandSigner(private_key)
    signature = signer.sign_wipe_command(action_id, payload.kiosk_id, timestamp, nonce)

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

    pool = await get_db()
    await pool.execute(
        "INSERT INTO remote_actions "
        "(id, kiosk_id, action_type, signed_payload, issued_by, status) "
        "VALUES ($1, $2, $3, $4, $5, $6)",
        uuid.UUID(action_id),
        payload.kiosk_id,
        "WIPE_FULL",
        signed_payload,
        admin_id,
        "PENDING",
    )

    logger.info(
        f"Wipe action {action_id} created for kiosk {payload.kiosk_id} "
        f"by admin {admin_id}"
    )

    return WipeResponse(
        action_id=action_id,
        kiosk_id=payload.kiosk_id,
        status="PENDING",
        signed_payload=signed_payload,
    )
