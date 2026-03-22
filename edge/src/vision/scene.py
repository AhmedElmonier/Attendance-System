import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PrimaryFaceSelector:
    def __init__(self, min_face_size: int = 100):
        self.min_face_size = min_face_size
        self.mp_face_detection = None
        self._init_detector()

    def _init_detector(self):
        try:
            import mediapipe as mp

            self.mp_face_detection = mp.solutions.face_detection
            self.detector = self.mp_face_detection.FaceDetection(
                model_selection=0, min_detection_confidence=0.5
            )
        except Exception as e:
            logger.warning(f"MediaPipe unavailable: {e}")

    def find_primary_face(
        self, frame: np.ndarray
    ) -> Optional[Tuple[np.ndarray, tuple]]:
        if hasattr(self, "detector") and self.detector:
            return self._find_with_mediapipe(frame)
        return self._find_largest_region(frame)

    def _find_with_mediapipe(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb)

        if not results.detections:
            return None

        h, w = frame.shape[:2]
        faces = []

        for detection in results.detections:
            box = detection.location_data.relative_bounding_box
            face_w = int(box.width * w)
            face_h = int(box.height * h)

            if face_w < self.min_face_size or face_h < self.min_face_size:
                continue

            faces.append(
                {
                    "box": (int(box.xmin * w), int(box.ymin * h), face_w, face_h),
                    "area": face_w * face_h,
                    "confidence": detection.score[0]
                    if hasattr(detection, "score")
                    else 1.0,
                }
            )

        if not faces:
            return None

        primary = max(faces, key=lambda x: x["area"] * x["confidence"])
        x, y, fw, fh = primary["box"]

        padding = int(max(fw, fh) * 0.15)
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(w, x + fw + padding)
        y2 = min(h, y + fh + padding)

        face_crop = frame[y1:y2, x1:x2]
        return face_crop, (x1, y1, x2, y2)

    def _find_largest_region(self, frame: np.ndarray):
        h, w = frame.shape[:2]
        face_h = int(h * 0.6)
        face_w = int(w * 0.4)
        y1 = (h - face_h) // 2
        x1 = (w - face_w) // 2
        y2 = y1 + face_h
        x2 = x1 + face_w

        face_crop = frame[y1:y2, x1:x2]
        return face_crop, (x1, y1, x2, y2)

    def close(self):
        if hasattr(self, "detector") and self.detector:
            self.detector.close()


class SceneAnalyzer:
    def __init__(self):
        self.face_selector = PrimaryFaceSelector()
        self.face_detector = None
        self._init_face_detector()

    def _init_face_detector(self):
        try:
            from edge.src.biometrics.embeddings import FaceDetector

            self.face_detector = FaceDetector()
        except Exception as e:
            logger.warning(f"FaceDetector unavailable: {e}")

    def analyze_frame(self, frame: np.ndarray) -> dict:
        result = {
            "has_primary_face": False,
            "face_crop": None,
            "face_box": None,
            "multiple_faces": False,
            "lighting_ok": True,
            "timestamp": None,
        }

        import time

        result["timestamp"] = time.time()

        primary = self.face_selector.find_primary_face(frame)
        if primary:
            result["has_primary_face"] = True
            result["face_crop"], result["face_box"] = primary

        result["lighting_ok"] = self._check_lighting(frame)

        return result

    def _check_lighting(self, frame: np.ndarray) -> bool:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        return 30 < brightness < 220

    def draw_analysis_overlay(self, frame: np.ndarray, analysis: dict) -> np.ndarray:
        output = frame.copy()

        if analysis["face_box"]:
            x1, y1, x2, y2 = analysis["face_box"]
            color = (0, 255, 0) if analysis["has_primary_face"] else (0, 0, 255)
            cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)

            if analysis["has_primary_face"]:
                h, w = output.shape[:2]
                label = "PRIMARY FACE"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.rectangle(
                    output,
                    (x1, y1 - label_size[1] - 10),
                    (x1 + label_size[0], y1),
                    (0, 255, 0),
                    -1,
                )
                cv2.putText(
                    output,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                )

        lighting_text = (
            "✓ Lighting OK" if analysis["lighting_ok"] else "⚠ Check Lighting"
        )
        lighting_color = (0, 255, 0) if analysis["lighting_ok"] else (0, 165, 255)
        cv2.putText(
            output,
            lighting_text,
            (10, output.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            lighting_color,
            2,
        )

        return output

    def close(self):
        if self.face_selector:
            self.face_selector.close()
        if self.face_detector:
            self.face_detector.close()
