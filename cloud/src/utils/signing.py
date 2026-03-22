import base64
import json
import logging
from typing import Dict, Any

import nacl.signing
import nacl.encoding

logger = logging.getLogger(__name__)


class WipeCommandSigner:
    def __init__(self, private_key_hex: str):
        self._signing_key = nacl.signing.SigningKey(bytes.fromhex(private_key_hex))

    def sign_wipe_command(
        self, action_id: str, kiosk_id: str, timestamp: str, nonce: str
    ) -> str:
        payload = json.dumps(
            {
                "action_id": action_id,
                "action": "WIPE_FULL",
                "kiosk_id": kiosk_id,
                "timestamp": timestamp,
                "nonce": nonce,
            },
            sort_keys=True,
        )
        signature = self._signing_key.sign(payload.encode("utf-8"))
        return base64.b64encode(signature.signature).decode("utf-8")

    def get_public_key_hex(self) -> str:
        return self._signing_key.verify_key.encode(nacl.encoding.HexEncoder).decode(
            "utf-8"
        )


class WipeCommandVerifier:
    def __init__(self, public_key_hex: str):
        self._verify_key = nacl.signing.VerifyKey(bytes.fromhex(public_key_hex))

    def verify_wipe_command(
        self,
        action_id: str,
        kiosk_id: str,
        timestamp: str,
        nonce: str,
        signature_b64: str,
    ) -> bool:
        payload = json.dumps(
            {
                "action_id": action_id,
                "action": "WIPE_FULL",
                "kiosk_id": kiosk_id,
                "timestamp": timestamp,
                "nonce": nonce,
            },
            sort_keys=True,
        )
        try:
            signature = base64.b64decode(signature_b64)
            self._verify_key.verify(payload.encode("utf-8"), signature)
            return True
        except (nacl.exceptions.BadSignatureError, Exception) as e:
            logger.warning(f"Wipe verification failed for kiosk {kiosk_id}: {e}")
            return False
