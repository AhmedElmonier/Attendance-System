import cv2
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class Frame:
    data: np.ndarray
    timestamp: float
    width: int
    height: int


class CameraBackend(ABC):
    @abstractmethod
    def open(self) -> bool:
        pass

    @abstractmethod
    def read(self) -> Optional[Frame]:
        pass

    @abstractmethod
    def release(self) -> None:
        pass

    @abstractmethod
    def is_opened(self) -> bool:
        pass


class DirectShowBackend(CameraBackend):
    def __init__(self, device_id: int = 0, width: int = 1280, height: int = 720):
        self.device_id = device_id
        self.width = width
        self.height = height
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        self._cap = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        if not self._cap.isOpened():
            self._cap = cv2.VideoCapture(self.device_id)
        if self._cap.isOpened():
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self._cap.set(cv2.CAP_PROP_FPS, 30)
            logger.info(f"Camera {self.device_id} opened: {self.width}x{self.height}")
            return True
        return False

    def read(self) -> Optional[Frame]:
        if not self._cap or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        if ret:
            return Frame(
                data=frame,
                timestamp=cv2.getTickCount() / cv2.getTickFrequency(),
                width=self.width,
                height=self.height,
            )
        return None

    def release(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None

    def is_opened(self) -> bool:
        return self._cap is not None and self._cap.isOpened()


class V4L2Backend(CameraBackend):
    def __init__(
        self, device_path: str = "/dev/video0", width: int = 1280, height: int = 720
    ):
        self.device_path = device_path
        self.width = width
        self.height = height
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        self._cap = cv2.VideoCapture(self.device_path, cv2.CAP_V4L2)
        if not self._cap.isOpened():
            self._cap = cv2.VideoCapture(self.device_path)
        if self._cap.isOpened():
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self._cap.set(cv2.CAP_PROP_FPS, 30)
            logger.info(f"Camera {self.device_path} opened: {self.width}x{self.height}")
            return True
        return False

    def read(self) -> Optional[Frame]:
        if not self._cap or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        if ret:
            return Frame(
                data=frame,
                timestamp=cv2.getTickCount() / cv2.getTickFrequency(),
                width=self.width,
                height=self.height,
            )
        return None

    def release(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None

    def is_opened(self) -> bool:
        return self._cap is not None and self._cap.isOpened()


class HALCamera:
    def __init__(self, backend: str = "auto", device_id: int = 0):
        self._backend: Optional[CameraBackend] = None
        self._backend_name = backend
        self._device_id = device_id
        self._select_backend()

    def _select_backend(self) -> None:
        import platform

        system = platform.system()

        if self._backend_name == "auto":
            if system == "Windows":
                self._backend_name = "dshow"
            elif system == "Linux":
                self._backend_name = "v4l2"
            else:
                self._backend_name = "default"

        if self._backend_name == "dshow":
            self._backend = DirectShowBackend(self._device_id)
        elif self._backend_name == "v4l2":
            self._backend = V4L2Backend(f"/dev/video{self._device_id}")
        elif self._backend_name == "simulator":
            self._backend = CameraSimulator()
        else:
            self._backend = DirectShowBackend(self._device_id)

    def start(self) -> bool:
        if self._backend:
            return self._backend.open()
        return False

    def capture(self) -> Optional[Frame]:
        if self._backend:
            return self._backend.read()
        return None

    def stop(self) -> None:
        if self._backend:
            self._backend.release()

    def is_active(self) -> bool:
        return self._backend is not None and self._backend.is_opened()


class CameraSimulator(CameraBackend):
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self._running = False
        self._tick = 0

    def open(self) -> bool:
        self._running = True
        logger.info("Camera simulator opened")
        return True

    def read(self) -> Optional[Frame]:
        if not self._running:
            return None
        self._tick += 1
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cv2.putText(
            frame,
            f"Simulated Frame {self._tick}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )
        return Frame(
            data=frame,
            timestamp=cv2.getTickCount() / cv2.getTickFrequency(),
            width=self.width,
            height=self.height,
        )

    def release(self) -> None:
        self._running = False

    def is_opened(self) -> bool:
        return self._running
