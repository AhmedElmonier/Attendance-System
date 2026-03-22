import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


@dataclass
class CapturedImage:
    pose: str
    image: np.ndarray
    quality_score: float
    yaw: float
    pitch: float


class ImageQualityChecker:
    MIN_RESOLUTION = (480, 480)
    MAX_BLUR_SCORE = 100.0
    MIN_BRIGHTNESS = 40
    MAX_BRIGHTNESS = 220

    def __init__(self):
        self.blur_threshold = self.MAX_BLUR_SCORE * 0.6

    def assess_quality(self, image: np.ndarray) -> tuple[bool, float, str]:
        if (
            image.shape[0] < self.MIN_RESOLUTION[0]
            or image.shape[1] < self.MIN_RESOLUTION[1]
        ):
            return False, 0.0, "Resolution too low"

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = self._calculate_blur(gray)
        if blur_score > self.blur_threshold:
            return False, blur_score, f"Image too blurry ({blur_score:.1f})"

        brightness = np.mean(gray)
        if brightness < self.MIN_BRIGHTNESS:
            return False, brightness, f"Too dark ({brightness:.0f})"
        if brightness > self.MAX_BRIGHTNESS:
            return False, brightness, f"Too bright ({brightness:.0f})"

        contrast = np.std(gray)
        if contrast < 30:
            return False, contrast, f"Low contrast ({contrast:.1f})"

        quality_score = min(
            1.0,
            (blur_score / self.MAX_BLUR_SCORE) * 0.4
            + (contrast / 100) * 0.3
            + (
                (brightness - self.MIN_BRIGHTNESS)
                / (self.MAX_BRIGHTNESS - self.MIN_BRIGHTNESS)
            )
            * 0.3,
        )

        return True, quality_score, "Good"

    def _calculate_blur(self, gray_image: np.ndarray) -> float:
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        return float(np.var(laplacian))


class EnrollmentWizard:
    POSE_SEQUENCE = ["center", "left", "right", "up", "down"]
    CAPTURES_PER_POSE = 3
    POSE_HOLD_FRAMES = 15
    CAPTURE_DELAY_FRAMES = 5

    def __init__(
        self, pose_detector, quality_checker: Optional[ImageQualityChecker] = None
    ):
        self.pose_detector = pose_detector
        self.quality_checker = quality_checker  # type: ignore
        self._reset_state()

    def _reset_state(self):
        self.captured_images: List[CapturedImage] = []
        self.current_pose_index = 0
        self.hold_frames = 0
        self.capture_delay = 0
        self.last_pose = None

    def get_current_pose(self) -> str:
        if self.current_pose_index < len(self.POSE_SEQUENCE):
            return self.POSE_SEQUENCE[self.current_pose_index]
        return "complete"

    def process_frame(self, frame: np.ndarray) -> tuple[str, np.ndarray]:
        if self.is_complete():
            return "complete", frame

        current_pose = self.get_current_pose()
        detected_pose = self.pose_detector.detect_pose(frame)

        if detected_pose is None:
            output = self._add_status_overlay(frame, "No face detected", (0, 0, 255))
            return current_pose, output

        is_valid = self.pose_detector.is_pose_valid(detected_pose, current_pose)
        direction, direction_text = self.pose_detector.get_pose_direction(detected_pose)

        output = self.pose_detector.draw_pose_overlay(
            frame, detected_pose, current_pose
        )
        output = self._add_status_overlay(
            output, f"Required pose: {current_pose.upper()}", (255, 255, 255)
        )
        output = self._add_status_overlay(
            output,
            direction_text,
            (255, 255, 0) if is_valid else (0, 165, 255),
            y_offset=120,
        )

        if is_valid:
            self.hold_frames += 1
            if self.hold_frames >= self.POSE_HOLD_FRAMES:
                self.capture_delay += 1
                if self.capture_delay >= self.CAPTURE_DELAY_FRAMES:
                    quality_ok, quality_score, quality_msg = (
                        self.quality_checker.assess_quality(frame)
                    )
                    if quality_ok:
                        self._capture(frame, detected_pose, quality_score)
                        self._next_pose()
                    output = self._add_status_overlay(
                        output,
                        quality_msg,
                        (0, 165, 255) if not quality_ok else (0, 255, 0),
                        y_offset=150,
                    )
        else:
            self.hold_frames = 0
            self.capture_delay = 0

        progress = len(self.captured_images)
        total = len(self.POSE_SEQUENCE) * self.CAPTURES_PER_POSE
        output = self._add_progress_bar(output, progress, total)

        return current_pose, output

    def _capture(self, frame: np.ndarray, pose, quality_score: float):
        self.captured_images.append(
            CapturedImage(
                pose=self.get_current_pose(),
                image=frame.copy(),
                quality_score=quality_score,
                yaw=pose.yaw,
                pitch=pose.pitch,
            )
        )
        logger.info(
            f"Captured {self.get_current_pose()} image. Total: {len(self.captured_images)}"
        )

    def _next_pose(self):
        current_captures = sum(
            1 for img in self.captured_images if img.pose == self.get_current_pose()
        )
        if current_captures >= self.CAPTURES_PER_POSE:
            self.current_pose_index += 1
        self.hold_frames = 0
        self.capture_delay = 0

    def _add_status_overlay(
        self, frame: np.ndarray, text: str, color: tuple, y_offset: int = 90
    ) -> np.ndarray:
        output = frame.copy()
        cv2.putText(
            output, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
        )
        return output

    def _add_progress_bar(
        self, frame: np.ndarray, current: int, total: int
    ) -> np.ndarray:
        output = frame.copy()
        h, w = frame.shape[:2]

        bar_width = 300
        bar_height = 20
        bar_x = (w - bar_width) // 2
        bar_y = h - 50

        cv2.rectangle(
            output,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (50, 50, 50),
            -1,
        )
        filled_width = int((current / max(1, total)) * bar_width)
        cv2.rectangle(
            output,
            (bar_x, bar_y),
            (bar_x + filled_width, bar_y + bar_height),
            (0, 200, 0),
            -1,
        )
        cv2.putText(
            output,
            f"Progress: {current}/{total}",
            (bar_x, bar_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

        return output

    def is_complete(self) -> bool:
        return self.current_pose_index >= len(self.POSE_SEQUENCE)

    def get_captures_by_pose(self, pose: str) -> List[CapturedImage]:
        return [img for img in self.captured_images if img.pose == pose]

    def get_best_capture(self, pose: str) -> Optional[CapturedImage]:
        captures = self.get_captures_by_pose(pose)
        if not captures:
            return None
        return max(captures, key=lambda x: x.quality_score)

    def get_summary(self) -> dict:
        return {
            "total_captures": len(self.captured_images),
            "captures_by_pose": {
                pose: len(self.get_captures_by_pose(pose))
                for pose in self.POSE_SEQUENCE
            },
            "all_complete": self.is_complete(),
            "is_valid": len(self.captured_images)
            >= len(self.POSE_SEQUENCE) * self.CAPTURES_PER_POSE,
        }
