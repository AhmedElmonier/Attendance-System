import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging
import hashlib
import onnxruntime as ort

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    vector: np.ndarray
    shape: tuple
    preprocessing_time_ms: float
    inference_time_ms: float


class EmbeddingExtractor:
    INPUT_SIZE = (112, 112)
    EMBEDDING_DIM = 512

    def __init__(self, model_path: Optional[str] = None):
        self.session: Optional[ort.InferenceSession] = None
        self.input_name: Optional[str] = None
        self.output_name: Optional[str] = None

        if model_path:
            self.load_model(model_path)
        else:
            self._init_placeholder_model()

    def _init_placeholder_model(self):
        logger.warning(
            "No model path provided. Using identity embedding as placeholder."
        )
        self._use_placeholder = True

    def load_model(self, model_path: str) -> None:
        try:
            providers = ["CPUExecutionProvider"]
            self.session = ort.InferenceSession(model_path, providers=providers)

            inputs = self.session.get_inputs()
            outputs = self.session.get_outputs()

            self.input_name = inputs[0].name if inputs else "input"
            self.output_name = outputs[0].name if outputs else "embedding"

            self._use_placeholder = False
            logger.info(f"Loaded embedding model from {model_path}")
        except ImportError:
            raise
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}. Using placeholder.")
            self._init_placeholder_model()

    def preprocess(self, face_crop: np.ndarray) -> Tuple[np.ndarray, float]:
        import time

        start = time.perf_counter()

        if face_crop.shape[:2] != self.INPUT_SIZE:
            face_crop = cv2.resize(face_crop, self.INPUT_SIZE)

        rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        normalized = (rgb.astype(np.float32) - 127.5) / 128.0

        batched = np.expand_dims(normalized, axis=0)

        preprocessing_time = (time.perf_counter() - start) * 1000
        return batched, preprocessing_time

    def extract(self, face_crop: np.ndarray) -> EmbeddingResult:
        import time

        preprocessed, preprocessing_time = self.preprocess(face_crop)

        if self._use_placeholder or self.session is None:
            embedding = self._create_placeholder_embedding(preprocessed)
            inference_time = 0.0
        else:
            infer_start = time.perf_counter()
            output = self.session.run(
                [self.output_name], {self.input_name: preprocessed}
            )
            embedding = output[0]
            inference_time = (time.perf_counter() - infer_start) * 1000

        embedding = embedding.flatten()
        embedding = embedding / np.linalg.norm(embedding)

        return EmbeddingResult(
            vector=embedding,
            shape=embedding.shape,
            preprocessing_time_ms=preprocessing_time,
            inference_time_ms=inference_time,
        )

    def _create_placeholder_embedding(self, preprocessed: np.ndarray) -> np.ndarray:
        data_hash = int(hashlib.sha256(preprocessed.tobytes()).hexdigest()[:12], 16)
        rng = np.random.default_rng(data_hash)
        embedding = rng.standard_normal(self.EMBEDDING_DIM).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.reshape(1, -1)

    def extract_batch(self, face_crops: List[np.ndarray]) -> List[EmbeddingResult]:
        return [self.extract(crop) for crop in face_crops]

    def extract_from_multiple_images(self, images: List[np.ndarray]) -> np.ndarray:
        embeddings = []
        for img in images:
            result = self.extract(img)
            embeddings.append(result.vector)
        return np.array(embeddings)


class FaceDetector:
    def __init__(self):
        self.mp_face_detection = None
        self._init_mediapipe()

    def _init_mediapipe(self):
        try:
            import mediapipe as mp

            self.mp_face_detection = mp.solutions.face_detection
            self.detector = self.mp_face_detection.FaceDetection(
                model_selection=0, min_detection_confidence=0.5
            )
            self._has_detector = True
        except Exception as e:
            logger.warning(f"MediaPipe face detection unavailable: {e}")
            self._has_detector = False

    def detect_face(self, frame: np.ndarray) -> Optional[tuple[np.ndarray, tuple]]:
        if self._has_detector and self.detector:
            return self._detect_with_mediapipe(frame)
        return self._detect_simple(frame)

    def _detect_with_mediapipe(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb)

        if not results.detections:
            return None

        h, w = frame.shape[:2]
        detection = results.detections[0]
        box = detection.location_data.relative_bounding_box

        x = int(box.xmin * w)
        y = int(box.ymin * h)
        box_w = int(box.width * w)
        box_h = int(box.height * h)

        padding = int(max(box_w, box_h) * 0.2)
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(w, x + box_w + padding)
        y2 = min(h, y + box_h + padding)

        face_crop = frame[y1:y2, x1:x2]

        if face_crop.size == 0:
            return None

        return face_crop, (x1, y1, x2, y2)

    def _detect_simple(self, frame: np.ndarray):
        h, w = frame.shape[:2]
        face_h = int(h * 0.5)
        face_w = int(w * 0.5)
        y1 = (h - face_h) // 2
        x1 = (w - face_w) // 2
        y2 = y1 + face_h
        x2 = x1 + face_w

        face_crop = frame[y1:y2, x1:x2]
        return face_crop, (x1, y1, x2, y2)

    def close(self):
        if hasattr(self, "detector") and self.detector:
            self.detector.close()
