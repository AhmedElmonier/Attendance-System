import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


GREEN_ZONE_THRESHOLD = 0.85
GRAY_ZONE_LOW = 0.75
GRAY_ZONE_HIGH = 0.85


class BiometricMatcher:
    def __init__(self, index, confidence_threshold: float = GREEN_ZONE_THRESHOLD):
        self.index = index
        self.confidence_threshold = confidence_threshold
        self.gray_zone_low = GRAY_ZONE_LOW
        self.gray_zone_high = GRAY_ZONE_HIGH

    def match(
        self, query_embedding: np.ndarray, k: int = 1
    ) -> Optional[Tuple[str, float, str]]:
        results = self.index.search(query_embedding, k)

        if not results:
            return None

        employee_id, confidence, _ = results[0]
        zone = self._classify_zone(confidence)

        return employee_id, confidence, zone

    def _classify_zone(self, confidence: float) -> str:
        if confidence >= self.confidence_threshold:
            return "green"
        elif confidence >= self.gray_zone_low:
            return "gray"
        else:
            return "red"

    def match_with_fallback(self, query_embedding: np.ndarray) -> dict:
        result = self.match(query_embedding)

        if result:
            employee_id, confidence, zone = result
            return {
                "matched": True,
                "employee_id": employee_id,
                "confidence": confidence,
                "zone": zone,
                "action": self._get_action(zone),
                "requires_review": zone != "green",
            }

        return {
            "matched": False,
            "employee_id": None,
            "confidence": 0.0,
            "zone": "red",
            "action": "reject",
            "requires_review": True,
        }

    def _get_action(self, zone: str) -> str:
        actions = {"green": "accept", "gray": "review", "red": "reject"}
        return actions.get(zone, "reject")

    def batch_match(self, query_embeddings: np.ndarray) -> list:
        results = []
        for embedding in query_embeddings:
            result = self.match_with_fallback(embedding)
            results.append(result)
        return results
