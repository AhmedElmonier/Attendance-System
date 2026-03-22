import cv2
import numpy as np
import mediapipe as mp
from dataclasses import dataclass
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class HeadPose:
    yaw: float
    pitch: float
    roll: float

    def is_within_threshold(
        self, yaw_threshold: float = 15.0, pitch_threshold: float = 10.0
    ) -> bool:
        return abs(self.yaw) <= yaw_threshold and abs(self.pitch) <= pitch_threshold


class PoseDetector:
    YAW_THRESHOLD = 15.0
    PITCH_THRESHOLD = 10.0
    ROLL_THRESHOLD = 15.0

    CENTER_YAW = 0.0
    LEFT_YAW = -30.0
    RIGHT_YAW = 30.0
    UP_PITCH = -15.0
    DOWN_PITCH = 15.0

    POSE_ANGLES = {
        "center": HeadPose(0, 0, 0),
        "left": HeadPose(-30, 0, 0),
        "right": HeadPose(30, 0, 0),
        "up": HeadPose(0, -15, 0),
        "down": HeadPose(0, 15, 0),
    }

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self._face_mesh = self._init_face_mesh()

    def _init_face_mesh(self):
        return self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect_pose(self, frame: np.ndarray) -> Optional[HeadPose]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None

        face_landmarks = results.multi_face_landmarks[0]
        pose = self._calculate_pose(face_landmarks, frame.shape)
        return pose

    def _calculate_pose(self, landmarks, image_shape) -> HeadPose:
        h, w = image_shape[:2]

        nose_tip = landmarks[1]
        nose_tip_x, nose_tip_y = int(nose_tip.x * w), int(nose_tip.y * h)

        left_eye_inner = landmarks[133]
        right_eye_inner = landmarks[362]

        left_eye_center_x = int(left_eye_inner.x * w)
        left_eye_center_y = int(left_eye_inner.y * h)
        right_eye_center_x = int(right_eye_inner.x * w)
        right_eye_center_y = int(right_eye_inner.y * h)

        eye_distance = np.sqrt(
            (right_eye_center_x - left_eye_center_x) ** 2
            + (right_eye_center_y - left_eye_center_y) ** 2
        )

        if eye_distance < 1e-6:
            eye_distance = 1e-6

        nose_to_left_eye_x = nose_tip_x - left_eye_center_x
        nose_to_left_eye_y = nose_tip_y - left_eye_center_y
        nose_to_right_eye_x = nose_tip_x - right_eye_center_x
        nose_to_right_eye_y = nose_tip_y - right_eye_center_y

        yaw = np.degrees(np.arctan2(nose_to_left_eye_x, nose_to_left_eye_y)) * 0.7
        yaw += np.degrees(np.arctan2(nose_to_right_eye_x, nose_to_right_eye_y)) * 0.3
        yaw = -yaw

        avg_eye_y = (left_eye_center_y + right_eye_center_y) / 2
        nose_to_eye_vertical = nose_tip_y - avg_eye_y
        focal_length = eye_distance * 2.5
        if focal_length < 1e-6:
            focal_length = 1e-6
        pitch = np.degrees(np.arctan2(nose_to_eye_vertical, focal_length)) * 0.8

        left_mouth_corner = landmarks[61]
        right_mouth_corner = landmarks[291]
        left_mouth_x = int(left_mouth_corner.x * w)
        right_mouth_x = int(right_mouth_corner.x * w)
        mouth_center_y = int((left_mouth_corner.y + right_mouth_corner.y) / 2 * h)

        roll = np.degrees(
            np.arctan2(mouth_center_y - avg_eye_y, right_mouth_x - left_mouth_x)
        )

        return HeadPose(yaw=yaw, pitch=pitch, roll=roll)

    def get_pose_direction(self, current_pose: HeadPose) -> Tuple[str, str]:
        yaw_diff = abs(current_pose.yaw)
        pitch_diff = abs(current_pose.pitch)

        if yaw_diff > pitch_diff:
            if current_pose.yaw < -self.YAW_THRESHOLD:
                return "turn_right", "Turn right →"
            elif current_pose.yaw > self.YAW_THRESHOLD:
                return "turn_left", "Turn left ←"
        else:
            if current_pose.pitch < -self.PITCH_THRESHOLD:
                return "tilt_up", "Tilt up ↑"
            elif current_pose.pitch > self.PITCH_THRESHOLD:
                return "tilt_down", "Tilt down ↓"

        return "centered", "Good position"

    def is_pose_valid(self, pose: HeadPose, target_pose: str) -> bool:
        target = self.POSE_ANGLES.get(target_pose)
        if not target:
            return False

        yaw_diff = abs(pose.yaw - target.yaw)
        pitch_diff = abs(pose.pitch - target.pitch)

        yaw_tolerance = 8.0 if target_pose == "center" else 12.0
        pitch_tolerance = 5.0 if target_pose == "center" else 8.0

        return yaw_diff <= yaw_tolerance and pitch_diff <= pitch_tolerance

    def draw_pose_overlay(
        self, frame: np.ndarray, pose: HeadPose, target_pose: str
    ) -> np.ndarray:
        output = frame.copy()

        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2

        cv2.putText(
            output,
            f"Yaw: {pose.yaw:.1f}° Pitch: {pose.pitch:.1f}° Roll: {pose.roll:.1f}°",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        target = self.POSE_ANGLES.get(target_pose, self.POSE_ANGLES["center"])
        cv2.putText(
            output,
            f"Target: {target_pose} (Yaw: {target.yaw}°, Pitch: {target.pitch}°)",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2,
        )

        is_valid = self.is_pose_valid(pose, target_pose)
        status_color = (0, 255, 0) if is_valid else (0, 165, 255)
        status_text = "[OK] Valid" if is_valid else "[X] Adjust position"
        cv2.putText(
            output,
            status_text,
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            status_color,
            2,
        )

        return output

    def close(self):
        self._face_mesh.close()
