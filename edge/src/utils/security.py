import base64
import json
import logging
from typing import Dict, Any

import nacl.signing
import nacl.encoding

logger = logging.getLogger(__name__)


class RemoteCommandVerifier:
    def __init__(self, public_key_hex: str):
        self._verify_key = nacl.signing.VerifyKey(
            bytes.fromhex(public_key_hex),
            encoder=nacl.encoding.HexEncoder,
        )

    def verify_command(self, payload: Dict[str, Any], signature_b64: str) -> bool:
        payload_str = json.dumps(payload, sort_keys=True)
        signature = base64.b64decode(signature_b64)
        try:
            self._verify_key.verify(payload_str.encode("utf-8"), signature)
            logger.info(
                f"Command verified: {payload.get('action', 'unknown')} "
                f"for {payload.get('kiosk_id', 'unknown')}"
            )
            return True
        except nacl.exceptions.BadSignatureError:
            logger.warning(
                f"Invalid command signature: {payload.get('action', 'unknown')}"
            )
            return False
