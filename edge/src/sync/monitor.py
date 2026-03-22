import requests
import time
from typing import Optional, List, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NetworkMonitor:
    CHECK_INTERVAL = 10
    RECOVERY确认_DELAY = 5

    def __init__(self, api_url: str = "https://api.attendance.local"):
        self.api_url = api_url
        self._is_online = False
        self._last_check = 0
        self._consecutive_failures = 0
        self._recovery_delay_counter = 0
        self._on_status_change: Optional[Callable[[bool], None]] = None

    def set_status_callback(self, callback: Callable[[bool], None]) -> None:
        self._on_status_change = callback

    def check_connectivity(self) -> bool:
        current_time = time.time()
        if (
            current_time - self._last_check < self.CHECK_INTERVAL
            and self._last_check > 0
        ):
            return self._is_online

        self._last_check = current_time

        try:
            response = requests.get(
                f"{self.api_url}/health", timeout=5, allow_redirects=False
            )
            is_online = response.status_code == 200
        except requests.exceptions.RequestException:
            is_online = False

        if is_online:
            self._consecutive_failures = 0
            self._recovery_delay_counter += 1

            if (
                not self._is_online
                and self._recovery_delay_counter >= self.RECOVERY确认_DELAY
            ):
                self._is_online = True
                self._notify_status_change(True)
        else:
            self._consecutive_failures += 1
            self._recovery_delay_counter = 0

            if self._is_online:
                self._is_online = False
                self._notify_status_change(False)

        return self._is_online

    def _notify_status_change(self, is_online: bool) -> None:
        logger.info(f"Network status changed: {'Online' if is_online else 'Offline'}")
        if self._on_status_change:
            self._on_status_change(is_online)

    def is_online(self) -> bool:
        return self._is_online

    def get_stats(self) -> dict:
        return {
            "is_online": self._is_online,
            "consecutive_failures": self._consecutive_failures,
            "last_check": self._last_check,
        }


class SyncTrigger:
    def __init__(self, monitor: NetworkMonitor, batcher, db, api_url: str):
        self.monitor = monitor
        self.batcher = batcher
        self.db = db
        self.api_url = api_url
        self._is_syncing = False

    def should_sync(self) -> bool:
        if not self.monitor.is_online():
            return False

        if self._is_syncing:
            return False

        pending = self.db.get_pending_logs(limit=1)
        return len(pending) > 0

    def trigger_sync(self, headers: Optional[dict] = None) -> dict:
        if not self.should_sync():
            return {"status": "skipped", "reason": "conditions_not_met"}

        self._is_syncing = True

        try:
            pending_logs = self.db.get_pending_logs(limit=self.batcher.batch_size)
            if not pending_logs:
                return {"status": "no_logs", "synced_count": 0}

            batch = self.batcher.create_batch(pending_logs)

            response = self._send_batch(batch, headers)

            if response.get("status") == "success":
                log_ids = [log.id for log in pending_logs]
                self.db.mark_logs_synced(log_ids)
                return {
                    "status": "success",
                    "synced_count": len(log_ids),
                    "batch_id": batch.batch_id,
                }
            else:
                return {
                    "status": "failed",
                    "error": response.get("error", "Unknown error"),
                }

        finally:
            self._is_syncing = False

    def _send_batch(self, batch, headers: Optional[dict] = None) -> dict:
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)

        try:
            response = requests.post(
                f"{self.api_url}/api/v1/sync/attendance",
                json=batch.to_dict(),
                headers=default_headers,
                timeout=30,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}

        except requests.exceptions.RequestException as e:
            logger.error(f"Sync request failed: {e}")
            return {"status": "error", "error": str(e)}
