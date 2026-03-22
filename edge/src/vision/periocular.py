import logging
from typing import Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)

EYE_LANDMARK_LEFT = 133
EYE_LANDMARK_RIGHT = 362
OCULAR_PADDING_RATIO = 0.3
OCULAR_ROI_MIN_SIZE = 48


class PeriocularCrop:
    def __init__(self, padding_ratio: float = OCULAR_PADDING_RATIO):
        self.padding_ratio = padding_ratio

    def extract_ocular_roi(
        self, frame: np.ndarray, landmarks: list
    ) -> Optional[np.ndarray]:
        if len(landmarks) <= max(EYE_LANDMARK_LEFT, EYE_LANDMARK_RIGHT):
            logger.warning("Insufficient landmarks for periocular extraction")
            return None

        left_eye = landmarks[EYE_LANDMARK_LEFT]
        right_eye = landmarks[EYE_LANDMARK_RIGHT]

        h, w = frame.shape[:2]
        lx, ly = int(left_eye.x * w), int(left_eye.y * h)
        rx, ry = int(right_eye.x * w), int(right_eye.y * h)

        eye_dist = abs(rx - lx)
        padding = int(eye_dist * self.padding_ratio)

        x_min = max(0, min(lx, rx) - padding)
        x_max = min(w, max(lx, rx) + padding)
        y_min = max(0, min(ly, ry) - padding * 2)
        y_max = min(h, max(ly, ry) + padding)

        if (x_max - x_min) < OCULAR_ROI_MIN_SIZE or (
            y_max - y_min
        ) < OCULAR_ROI_MIN_SIZE:
            logger.warning(
                f"ROI too small: {x_max - x_min}x{y_max - y_min}, "
                f"minimum {OCULAR_ROI_MIN_SIZE}px"
            )
            return None

        roi = frame[y_min:y_max, x_min:x_max]

        if roi.size == 0:
            return None

        roi_resized = cv2.resize(roi, (224, 224))

        logger.debug(f"Periocular ROI extracted: {roi.shape} -> 224x224")
        return roi_resized

    def detect_face_covering(self, landmarks: list, lower_confidence: float) -> bool:
        if lower_confidence < 0.3:
            logger.info("Face covering detected (low mouth confidence)")
            return True
        return False
