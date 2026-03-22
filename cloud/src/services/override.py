import logging
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class OverrideService:
    def __init__(self, db_session):
        self.db = db_session

    def process_override(
        self,
        event_id: str,
        action: str,
        manager_id: UUID,
        reason: Optional[str] = None,
    ) -> dict:
        if action == "approve" and not reason:
            raise ValueError("A reason is required for approval overrides")

        result = {
            "event_id": event_id,
            "action": action,
            "reviewed_by": str(manager_id),
            "reason": reason,
            "status": "processed",
        }

        logger.info(
            f"Override service: {action} event={event_id} "
            f"by manager={manager_id} reason={reason}"
        )
        return result
