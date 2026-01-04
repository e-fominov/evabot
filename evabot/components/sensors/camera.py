"""
Orbbec 3D Camera sensor component.
Provides easy access to RGB and Depth camera data for robots.
"""

import logging
from typing import Optional, Tuple
import numpy as np
from evabot.components.base import Component
from evabot.hardware import CameraDevice


logger = logging.getLogger(__name__)


class OrbbecCamera(Component):
    """
    Orbbec 3D Camera component (RGB + Depth).

    Provides easy access to camera frames:
    - RGB color image
    - Depth map
    - Distance at specific pixel
    - Works standalone or attached to Robot

    Example (standalone):
        >>> camera = OrbbecCamera()
        >>> camera.start()
        >>> rgb = camera.image
        >>> depth = camera.depth
        >>> camera.stop()

    Example (with robot):
        >>> robot = Robot()
        >>> robot.camera = OrbbecCamera()
        >>> robot.start()
        >>> print(f"RGB shape: {robot.camera.image.shape}")
        >>> distance = robot.camera.depth_at(320, 240)
    """

    def __init__(self, device: Optional[CameraDevice] = None,
                 device_id: int = 0,
                 rgb_width: int = 640, rgb_height: int = 480,
                 depth_width: int = 640, depth_height: int = 480,
                 fps: int = 30):
        """
        Initialize Orbbec camera component.

        Args:
            device: Optional CameraDevice instance (uses singleton if None)
            device_id: Camera device index (default 0)
            rgb_width: RGB frame width (default 640)
            rgb_height: RGB frame height (default 480)
            depth_width: Depth frame width (default 640)
            depth_height: Depth frame height (default 480)
            fps: Frame rate (default 30)
        """
        super().__init__()

        # Get or use camera device (singleton)
        if device is None:
            self._device = CameraDevice.get_default(device_id=device_id)
        else:
            self._device = device

        # Stream configuration
        self._rgb_width = rgb_width
        self._rgb_height = rgb_height
        self._depth_width = depth_width
        self._depth_height = depth_height
        self._fps = fps

        logger.info("OrbbecCamera component created")

    def start(self):
        """Start camera capture."""
        logger.info("Starting OrbbecCamera...")
        self._device.start(
            rgb_width=self._rgb_width,
            rgb_height=self._rgb_height,
            depth_width=self._depth_width,
            depth_height=self._depth_height,
            fps=self._fps
        )
        self._running = True
        logger.info("OrbbecCamera started")

    def stop(self):
        """Stop camera capture."""
        logger.info("Stopping OrbbecCamera...")
        self._running = False
        # Note: Don't stop the device - other components might be using it
        # The device will be stopped by cleanup_all() on exit
        logger.info("OrbbecCamera stopped")

    @property
    def image(self) -> Optional[np.ndarray]:
        """
        Get latest RGB image.

        Returns:
            RGB image as numpy array (H, W, 3) with dtype uint8,
            or None if no frame available

        Example:
            >>> rgb = camera.image
            >>> if rgb is not None:
            >>>     cv2.imshow('Camera', rgb)
        """
        return self._device.get_latest_rgb()

    @property
    def depth(self) -> Optional[np.ndarray]:
        """
        Get latest depth map.

        Returns:
            Depth image as numpy array (H, W) with dtype uint16,
            values in millimeters, or None if no frame available

        Example:
            >>> depth = camera.depth
            >>> if depth is not None:
            >>>     # Normalize for visualization
            >>>     depth_viz = (depth / depth.max() * 255).astype(np.uint8)
            >>>     cv2.imshow('Depth', depth_viz)
        """
        return self._device.get_latest_depth()

    @property
    def depth_meters(self) -> Optional[np.ndarray]:
        """
        Get latest depth map in meters (instead of millimeters).

        Returns:
            Depth image as numpy array (H, W) with dtype float32,
            values in meters, or None if no frame available

        Example:
            >>> depth_m = camera.depth_meters
            >>> if depth_m is not None:
            >>>     print(f"Range: {depth_m.min():.2f}m to {depth_m.max():.2f}m")
        """
        depth_mm = self._device.get_latest_depth()
        if depth_mm is None:
            return None
        return (depth_mm / 1000.0).astype(np.float32)

    def depth_at(self, x: int, y: int) -> Optional[float]:
        """
        Get depth at specific pixel (in meters).

        Args:
            x: Pixel x coordinate (0 = left)
            y: Pixel y coordinate (0 = top)

        Returns:
            Distance in meters, or None if no depth data or out of bounds

        Example:
            >>> # Get distance at center of image
            >>> distance = camera.depth_at(320, 240)
            >>> if distance is not None:
            >>>     print(f"Object at center is {distance:.2f}m away")
        """
        depth_mm = self._device.get_latest_depth()
        if depth_mm is None:
            return None

        # Check bounds
        height, width = depth_mm.shape
        if x < 0 or x >= width or y < 0 or y >= height:
            logger.warning(f"Pixel ({x}, {y}) out of bounds ({width}x{height})")
            return None

        # Get depth value (millimeters → meters)
        depth_value_mm = depth_mm[y, x]
        if depth_value_mm == 0:
            return None  # No depth reading at this pixel

        return depth_value_mm / 1000.0

    def get_frames(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Get both RGB and depth frames atomically.

        Returns:
            Tuple of (rgb_image, depth_image), either may be None

        Example:
            >>> rgb, depth = camera.get_frames()
            >>> if rgb is not None and depth is not None:
            >>>     # Process RGB and depth together
            >>>     aligned_data = process_rgbd(rgb, depth)
        """
        return self._device.get_latest_frames()

    @property
    def is_connected(self) -> bool:
        """Check if camera is connected and running."""
        return self._device.is_connected

    @property
    def resolution_rgb(self) -> Tuple[int, int]:
        """Get RGB resolution (width, height)."""
        return (self._rgb_width, self._rgb_height)

    @property
    def resolution_depth(self) -> Tuple[int, int]:
        """Get depth resolution (width, height)."""
        return (self._depth_width, self._depth_height)

    @property
    def frame_rate(self) -> int:
        """Get configured frame rate."""
        return self._fps
