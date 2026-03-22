import json
import logging
import os
from typing import Optional

from edge.src.utils.security import RemoteCommandVerifier

logger = logging.getLogger(__name__)


class SecureWipeExecutor:
    def __init__(self, db, index_path: Optional[str] = None):
        self.db = db
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

        verifier = RemoteCommandVerifier(public_key)
        if not verifier.verify_command(payload, signature):
            return {"status": "FAILED", "reason": "Invalid signature"}

        kiosk_id = payload.get("kiosk_id")
        logger.warning(f"Executing secure wipe for kiosk {kiosk_id}")

        try:
            conn = self.db._get_connection()

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
            return {"status": "FAILED", "reason": str(e)}
