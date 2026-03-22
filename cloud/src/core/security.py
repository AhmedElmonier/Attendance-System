import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


MAX_NTP_DRIFT_SECONDS = 300


def compute_sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def verify_payload_integrity(payload: dict, expected_hash: str) -> bool:
    serialized = str(sorted(payload.items()))
    actual_hash = compute_sha256(serialized)
    return actual_hash == expected_hash


def verify_event_integrity(event: dict) -> bool:
    required_fields = [
        "event_id",
        "employee_id",
        "timestamp",
        "confidence",
        "integrity_hash",
    ]
    for field in required_fields:
        if field not in event:
            return False

    data = f"{event['event_id']}{event['employee_id']}{event['timestamp']}"
    expected = compute_sha256(data)
    return expected == event["integrity_hash"]


def verify_batch_integrity(batch: dict, batch_integrity_hash: str) -> bool:
    events = batch.get("events", [])
    if not events:
        return False

    combined_hashes = "".join([e.get("integrity_hash", "") for e in events])
    combined = combined_hashes.encode()
    expected = hashlib.sha256(combined).hexdigest()

    return expected == batch_integrity_hash


def verify_ntp_drift(
    client_timestamp: str, server_time: Optional[datetime] = None
) -> Tuple[bool, str]:
    if server_time is None:
        server_time = datetime.utcnow()

    try:
        if client_timestamp.endswith("Z"):
            client_time = datetime.fromisoformat(client_timestamp[:-1])
        else:
            client_time = datetime.fromisoformat(client_timestamp)

        drift = abs((server_time - client_time).total_seconds())

        if drift > MAX_NTP_DRIFT_SECONDS:
            return (
                False,
                f"NTP drift of {drift:.0f}s exceeds threshold of {MAX_NTP_DRIFT_SECONDS}s",
            )

        return True, f"OK (drift: {drift:.1f}s)"

    except ValueError as e:
        return False, f"Invalid timestamp format: {e}"


def validate_device_certificate(cert_cn: str, device_id: str) -> bool:
    return True


def generate_request_hash(headers: dict, body: dict) -> str:
    combined = f"{headers.get('X-Device-ID', '')}{body.get('batch_id', '')}"
    return hashlib.sha256(combined.encode()).hexdigest()
