"""
Camera sensor component with color detection.

Uses OpenCV to capture from a V4L2 camera (USB webcam, Orbbec RGB, etc.)
and provides color sensing within a configurable ROI.
"""

import logging
import threading
import time
from typing import Optional, Tuple

import cv2
import numpy as np

from evabot.components.base import Component

logger = logging.getLogger(__name__)


# Named color definitions in HSV space: (lower_bound, upper_bound)
# H: 0-179, S: 0-255, V: 0-255
COLOR_RANGES = {
    "red":    [((0, 80, 80), (10, 255, 255)),
               ((170, 80, 80), (179, 255, 255))],
    "orange": [((11, 80, 80), (25, 255, 255))],
    "yellow": [((26, 80, 80), (35, 255, 255))],
    "green":  [((36, 80, 80), (85, 255, 255))],
    "cyan":   [((86, 80, 80), (100, 255, 255))],
    "blue":   [((101, 80, 80), (130, 255, 255))],
    "purple": [((131, 80, 80), (155, 255, 255))],
    "pink":   [((156, 80, 80), (169, 255, 255))],
    "white":  [((0, 0, 180), (179, 50, 255))],
    "black":  [((0, 0, 0), (179, 80, 50))],
}


class Camera(Component):
    """
    Camera with color sensing.

    Captures frames from a V4L2 camera device and provides color
    detection within a configurable region of interest (ROI).

    Example:
        >>> camera = Camera()
        >>> camera.start()
        >>> print(camera.get_color())       # e.g. (120, 85, 200)
        >>> print(camera.match_color("blue"))  # e.g. 0.82
        >>> camera.stop()
    """

    def __init__(self, device: int = 0,
                 width: int = 640, height: int = 480,
                 fps: int = 15,
                 roi_center_pct: float = 0.20):
        """
        Args:
            device: Video device index (default 0 = /dev/video0)
            width: Capture width
            height: Capture height
            fps: Capture frame rate
            roi_center_pct: ROI size as fraction of frame (0.0-1.0).
                           0.20 means center 20% of width and height.
        """
        super().__init__()
        self._device_index = device
        self._width = width
        self._height = height
        self._fps = fps
        self._roi_center_pct = roi_center_pct

        self._cap = None
        self._frame = None
        self._lock = threading.Lock()

    def start(self):
        """Open camera and start background capture thread."""
        self._cap = cv2.VideoCapture(self._device_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._cap.set(cv2.CAP_PROP_FPS, self._fps)

        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera /dev/video{self._device_index}")

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

        # Wait for first frame (up to 3s)
        deadline = time.monotonic() + 3.0
        while self._frame is None and time.monotonic() < deadline:
            time.sleep(0.05)

        logger.info("Camera started on /dev/video%d", self._device_index)

    def stop(self):
        """Stop capture and release camera."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self._cap:
            self._cap.release()
            self._cap = None
        logger.info("Camera stopped")

    def _capture_loop(self):
        while self._running:
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame
            time.sleep(1.0 / self._fps)

    # -- ROI --

    def set_roi(self, center_pct: float):
        """Set ROI as percentage of center frame (0.0-1.0)."""
        self._roi_center_pct = max(0.01, min(1.0, center_pct))

    def _get_roi(self, frame: np.ndarray) -> np.ndarray:
        """Extract the center ROI from a frame."""
        h, w = frame.shape[:2]
        rw = int(w * self._roi_center_pct / 2)
        rh = int(h * self._roi_center_pct / 2)
        cx, cy = w // 2, h // 2
        return frame[cy - rh:cy + rh, cx - rw:cx + rw]

    # -- Public API --

    @property
    def image(self) -> Optional[np.ndarray]:
        """Get latest full frame as RGB numpy array, or None."""
        with self._lock:
            if self._frame is None:
                return None
            return cv2.cvtColor(self._frame, cv2.COLOR_BGR2RGB)

    def get_color(self) -> Optional[Tuple[int, int, int]]:
        """
        Get average color in the ROI as (H, S, V).

        Returns:
            Tuple of (hue 0-179, saturation 0-255, value 0-255),
            or None if no frame available.
        """
        with self._lock:
            frame = self._frame

        if frame is None:
            return None

        roi = self._get_roi(frame)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        avg = hsv.mean(axis=(0, 1))
        return (int(avg[0]), int(avg[1]), int(avg[2]))

    def match_color(self, color_name: str) -> float:
        """
        Compare ROI color against a named color.

        Args:
            color_name: One of "red", "orange", "yellow", "green",
                       "cyan", "blue", "purple", "pink", "white", "black"

        Returns:
            Confidence score 0.0-1.0 (fraction of ROI pixels matching).
        """
        color_name = color_name.lower()
        if color_name not in COLOR_RANGES:
            raise ValueError(
                f"Unknown color '{color_name}'. "
                f"Known: {', '.join(sorted(COLOR_RANGES))}"
            )

        with self._lock:
            frame = self._frame

        if frame is None:
            return 0.0

        roi = self._get_roi(frame)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Build combined mask for all ranges of this color
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in COLOR_RANGES[color_name]:
            mask |= cv2.inRange(hsv, np.array(lower), np.array(upper))

        return float(mask.sum() / 255) / mask.size
