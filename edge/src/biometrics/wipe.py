import json
import logging
import os
import time
from typing import Optional, Dict, Set

from edge.src.utils.security import RemoteCommandVerifier

logger = logging.getLogger(__name__)

_nonce_store: Dict[str, float] = {}
_nonce_ttl = 600


def _is_nonce_used(nonce: str) -> bool:
    now = time.time()
    expired = [n for n, t in _nonce_store.items() if now - t > _nonce_ttl]
    for n in expired:
        del _nonce_store[n]
    return nonce in _nonce_store


def _record_nonce(nonce: str) -> None:
    _nonce_store[nonce] = time.time()


class SecureWipeExecutor:
    def __init__(self, db, kiosk_id: str, index_path: Optional[str] = None):
        self.db = db
        self.kiosk_id = kiosk_id
        self.index_path = index_path

    def execute_wipe(self, signed_payload_str: str) -> dict:
        public_key = os.getenv("ED25519_PUBLIC_KEY")
        if not public_key:
            raise RuntimeError("ED25519_PUBLIC_KEY not configured")

        try:
            payload = json.loads(signed_payload_str)
        except json.JSONDecodeError:
            return {"status": "FAILED", "reason": "Invalid payload JSON"}

        signature = payload.pop("signature", "")
        if not signature:
            return {"status": "FAILED", "reason": "Missing signature"}

        if payload.get("kiosk_id") != self.kiosk_id:
            logger.warning(
                f"Wipe rejected: kiosk mismatch "
                f"(expected={self.kiosk_id}, got={payload.get('kiosk_id')})"
            )
            return {"status": "FAILED", "reason": "Kiosk ID mismatch"}

        timestamp = payload.get("timestamp", "")
        nonce = payload.get("nonce", "")
        try:
            ts = __import__("datetime").datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            age = abs((now - ts).total_seconds())
            if age > 300:
                logger.warning(f"Wipe rejected: timestamp age {age}s > 300s")
                return {"status": "FAILED", "reason": "Timestamp too old"}
        except Exception:
            return {"status": "FAILED", "reason": "Invalid timestamp"}

        if _is_nonce_used(nonce):
            logger.warning(f"Wipe rejected: nonce {nonce} already used")
            return {"status": "FAILED", "reason": "Nonce already used"}

        verifier = RemoteCommandVerifier(public_key)
        if not verifier.verify_command(payload, signature):
            return {"status": "FAILED", "reason": "Invalid signature"}

        _record_nonce(nonce)

        kiosk_id = payload.get("kiosk_id")
        logger.warning(f"Executing secure wipe for kiosk {kiosk_id}")

        try:
            conn = self.db.get_connection()

            cursor = conn.execute("SELECT COUNT(*) FROM biometric_templates")
            template_count = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM attendance_logs")
            log_count = cursor.fetchone()[0]

            conn.execute("DELETE FROM biometric_templates")
            conn.execute("DELETE FROM attendance_logs")
            conn.execute(
                "UPDATE employees SET status = 'pending_sync' WHERE status = 'active'"
            )
            conn.commit()

            conn.execute("VACUUM")
            conn.commit()

            if self.index_path and os.path.exists(self.index_path):
                os.remove(self.index_path)
                logger.info(f"HNSW index cleared: {self.index_path}")

            logger.warning(
                f"Wipe complete: {template_count} templates, {log_count} logs cleared"
            )

            return {
                "status": "VERIFIED",
                "templates_cleared": template_count,
                "logs_cleared": log_count,
            }

        except Exception as e:
            logger.exception(f"Wipe execution failed: {e}")
            return {"status": "FAILED", "reason": "Wipe execution error"}
