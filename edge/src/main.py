import cv2
import argparse
import logging
import os
import sys
import yaml
import numpy as np

from edge.src.hal.camera import HALCamera
from edge.src.hal.feedback import FeedbackModule
from edge.src.vision.pose import PoseDetector
from edge.src.vision.enrollment import EnrollmentWizard
from edge.src.vision.scene import SceneAnalyzer
from edge.src.biometrics.embeddings import EmbeddingExtractor, FaceDetector
from edge.src.biometrics.index import VectorIndex
from edge.src.biometrics.matcher import BiometricMatcher
from edge.src.storage.db import create_db, EncryptedDB

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AttendanceSystem:
    def __init__(self, config_path: str = "edge/config.yaml"):
        self.config = self._load_config(config_path)
        self.db = self._init_database()
        self.camera = self._init_camera()
        self.feedback = FeedbackModule(language="en")
        self.index = VectorIndex(embedding_dim=512, space="cosine")
        self.matcher = BiometricMatcher(self.index)
        self._load_existing_templates()

    def _load_config(self, config_path: str) -> dict:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return {}

    def _init_database(self) -> EncryptedDB:
        db_key = os.environ.get("ATTENDANCE_DB_KEY")
        if not db_key:
            logger.error("ATTENDANCE_DB_KEY environment variable is required")
            raise RuntimeError(
                "ATTENDANCE_DB_KEY environment variable is required. "
                "Set it before running the application."
            )
        db_path = self.config.get("database", {}).get("path", "edge/data/attendance.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return create_db(db_path, db_key)

    def _init_camera(self) -> HALCamera:
        hal_config = self.config.get("hal", {})
        backend = hal_config.get("input", "webcam")
        return HALCamera(backend=backend)

    def _load_existing_templates(self):
        templates = self.db.get_all_biometric_templates()
        for tmpl in templates:
            vector = tmpl.vector_blob
            if isinstance(vector, bytes):
                import numpy as np

                vector = np.frombuffer(vector, dtype=np.float32)
            self.index.add(tmpl.employee_id, vector)
        logger.info(f"Loaded {len(templates)} existing biometric templates")

    def run_enrollment(self, name_ar: str = "", name_en: str = ""):
        logger.info("Starting enrollment mode")

        if not name_en:
            name_en = input("Enter employee name (English): ")
        if not name_ar:
            name_ar = input("Enter employee name (Arabic): ")

        employee = self.db.add_employee(name_ar=name_ar, name_en=name_en)
        logger.info(f"Created employee record: {employee.id}")

        pose_detector = PoseDetector()
        wizard = EnrollmentWizard(pose_detector)

        if not self.camera.start():
            logger.error("Failed to start camera")
            return False

        try:
            while not wizard.is_complete():
                frame = self.camera.capture()
                if frame is None:
                    continue

                pose, output = wizard.process_frame(frame.data)

                cv2.imshow("Enrollment - Press 'q' to quit", output)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

        finally:
            self.camera.stop()
            cv2.destroyAllWindows()
            pose_detector.close()

        summary = wizard.get_summary()
        logger.info(f"Enrollment summary: {summary}")

        if not summary["is_valid"]:
            logger.warning("Enrollment incomplete")
            return False

        self._store_enrollment(wizard, employee.id)
        self.feedback.set_status("enrollment_success", "green")
        logger.info(f"Enrollment complete for {name_en}")
        return True

    def _store_enrollment(self, wizard: EnrollmentWizard, employee_id: str):
        extractor = EmbeddingExtractor()
        detector = FaceDetector()

        for pose in ["center", "left", "right", "up", "down"]:
            best_capture = wizard.get_best_capture(pose)
            if best_capture is None:
                continue

            face_data = detector.detect_face(best_capture.image)
            if face_data is None:
                continue

            face_crop = face_data[0]
            result = extractor.extract(face_crop)

            vector_bytes = result.vector.astype(np.float32).tobytes()
            self.db.add_biometric_template(employee_id, vector_bytes, pose)
            self.index.add(employee_id, result.vector)

            logger.info(f"Stored template for {pose}: {result.vector.shape}")

    def run_clock_in(self):
        logger.info("Starting clock-in mode")

        pose_detector = PoseDetector()
        scene_analyzer = SceneAnalyzer()
        extractor = EmbeddingExtractor()
        detector = FaceDetector()

        if not self.camera.start():
            logger.error("Failed to start camera")
            return

        try:
            while True:
                frame = self.camera.capture()
                if frame is None:
                    continue

                scene = scene_analyzer.analyze_frame(frame.data)
                output = scene_analyzer.draw_analysis_overlay(frame.data, scene)

                if scene["has_primary_face"] and scene["face_crop"] is not None:
                    result = extractor.extract(scene["face_crop"])
                    match_result = self.matcher.match_with_fallback(result.vector)

                    feedback_text, color = self.feedback.get_zone_feedback(
                        match_result["zone"]
                    )
                    cv2.putText(
                        output,
                        feedback_text,
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        color,
                        2,
                    )

                    if match_result["matched"]:
                        log = self.db.add_attendance_log(
                            match_result["employee_id"],
                            match_result["confidence"],
                            match_result["zone"],
                            match_result.get("requires_review", False),
                        )
                        logger.info(
                            f"Clock-in recorded: {log.id} (confidence: {match_result['confidence']:.3f})"
                        )

                        if match_result["zone"] == "green":
                            break
                        elif match_result["zone"] == "gray":
                            logger.warning(
                                f"Gray zone match requires review: {match_result['employee_id']}"
                            )
                            break

                cv2.imshow("Clock-In - Press 'q' to quit", output)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

        finally:
            self.camera.stop()
            cv2.destroyAllWindows()
            pose_detector.close()
            scene_analyzer.close()
            detector.close()


def main():
    parser = argparse.ArgumentParser(description="Attendance System Edge Device")
    parser.add_argument(
        "--mode",
        choices=["enroll", "clock-in", "clock-in-enroll"],
        default="clock-in",
        help="Operation mode",
    )
    parser.add_argument("--config", default="edge/config.yaml", help="Config file path")
    parser.add_argument("--name-en", help="Employee name (English)")
    parser.add_argument("--name-ar", help="Employee name (Arabic)")
    parser.add_argument(
        "--language", choices=["en", "ar"], default="en", help="UI language"
    )

    args = parser.parse_args()

    system = AttendanceSystem(config_path=args.config)
    system.feedback.set_language(args.language)

    if args.mode in ["enroll", "clock-in-enroll"]:
        success = system.run_enrollment(
            name_ar=args.name_ar or "", name_en=args.name_en or ""
        )
        if not success:
            logger.error("Enrollment failed")
            sys.exit(1)

    if args.mode in ["clock-in", "clock-in-enroll"]:
        system.run_clock_in()


if __name__ == "__main__":
    main()
