import uuid
import hashlib
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class SyncBatch:
    batch_id: str
    events: List[Dict[str, Any]]
    kiosk_timestamp: str
    integrity_hash: str

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "events": self.events,
            "kiosk_timestamp": self.kiosk_timestamp,
            "integrity_hash": self.integrity_hash,
        }


class BatchCreator:
    def __init__(self, batch_size: int = 500):
        self.batch_size = batch_size

    def create_batch(self, logs: List[Any]) -> SyncBatch:
        events = []
        for log in logs:
            event_dict = {
                "event_id": log.id if hasattr(log, "id") else str(log),
                "employee_id": log.employee_id if hasattr(log, "employee_id") else "",
                "timestamp": log.timestamp.isoformat()
                if hasattr(log, "timestamp") and isinstance(log.timestamp, datetime)
                else str(log.timestamp),
                "confidence": float(log.confidence)
                if hasattr(log, "confidence")
                else 0.0,
                "integrity_hash": self._generate_event_hash(log),
            }
            events.append(event_dict)

        batch_id = str(uuid.uuid4())
        kiosk_timestamp = datetime.utcnow().isoformat() + "Z"
        integrity_hash = self._generate_batch_hash(events)

        return SyncBatch(
            batch_id=batch_id,
            events=events,
            kiosk_timestamp=kiosk_timestamp,
            integrity_hash=integrity_hash,
        )

    def create_batches(self, logs: List[Any]) -> List[SyncBatch]:
        batches = []
        for i in range(0, len(logs), self.batch_size):
            chunk = logs[i : i + self.batch_size]
            batch = self.create_batch(chunk)
            batches.append(batch)
        return batches

    def _generate_event_hash(self, event: Any) -> str:
        data = f"{event.id if hasattr(event, 'id') else ''}{event.employee_id if hasattr(event, 'employee_id') else ''}{event.timestamp if hasattr(event, 'timestamp') else ''}".encode()
        return hashlib.sha256(data).hexdigest()

    def _generate_batch_hash(self, events: List[Dict[str, Any]]) -> str:
        combined = "".join([e["integrity_hash"] for e in events])
        return hashlib.sha256(combined.encode()).hexdigest()

    def verify_batch_integrity(self, batch: SyncBatch) -> bool:
        expected_hash = self._generate_batch_hash(batch.events)
        return batch.integrity_hash == expected_hash
