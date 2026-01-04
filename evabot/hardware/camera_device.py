"""
Orbbec camera hardware device (singleton) using C SDK via ctypes.
Manages physical Orbbec 3D camera connection.
"""

import logging
import threading
import time
import atexit
from typing import Optional, Tuple
from ctypes import *
import numpy as np
import os

logger = logging.getLogger(__name__)

# Try to import cv2 for MJPG decoding
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV not available - MJPG color frames will not be decoded")

# OrbbecSDK library path
SDK_LIB_PATH = "/home/fm/work/OrbbecSDK/lib/linux_x64/libOrbbecSDK.so"

# Check if library exists
if not os.path.exists(SDK_LIB_PATH):
    raise RuntimeError(f"OrbbecSDK library not found at {SDK_LIB_PATH}")

# Load OrbbecSDK library
try:
    ob = CDLL(SDK_LIB_PATH)
    HAS_ORBBEC = True
except OSError as e:
    logger.error(f"Failed to load OrbbecSDK: {e}")
    HAS_ORBBEC = False
    ob = None


# ========== ctypes Structures and Enums ==========

class ob_error(Structure):
    _fields_ = [
        ("status", c_int),
        ("message", c_char * 256),
        ("function", c_char * 256),
        ("args", c_char * 256),
        ("exception_type", c_int),
    ]


# Opaque pointers (handles)
class ob_context(Structure):
    pass


class ob_device(Structure):
    pass


class ob_device_list(Structure):
    pass


class ob_pipeline(Structure):
    pass


class ob_config(Structure):
    pass


class ob_frame(Structure):
    pass


# Enums
OB_STREAM_COLOR = 2
OB_STREAM_DEPTH = 3

OB_FORMAT_RGB = 22
OB_FORMAT_Y16 = 8
OB_FORMAT_MJPG = 5
OB_FORMAT_ANY = 0xFF  # OB_FORMAT_UNKNOWN

# Defaults for "any" parameter
OB_WIDTH_ANY = 0
OB_HEIGHT_ANY = 0
OB_FPS_ANY = 0


# ========== Function Signatures ==========

# Context functions
ob.ob_create_context.argtypes = [POINTER(POINTER(ob_error))]
ob.ob_create_context.restype = POINTER(ob_context)

ob.ob_delete_context.argtypes = [POINTER(ob_context), POINTER(POINTER(ob_error))]
ob.ob_delete_context.restype = None

ob.ob_query_device_list.argtypes = [POINTER(ob_context), POINTER(POINTER(ob_error))]
ob.ob_query_device_list.restype = POINTER(ob_device_list)

# Device list functions
ob.ob_device_list_device_count.argtypes = [POINTER(ob_device_list), POINTER(POINTER(ob_error))]
ob.ob_device_list_device_count.restype = c_uint32

ob.ob_device_list_get_device.argtypes = [POINTER(ob_device_list), c_uint32, POINTER(POINTER(ob_error))]
ob.ob_device_list_get_device.restype = POINTER(ob_device)

ob.ob_delete_device_list.argtypes = [POINTER(ob_device_list), POINTER(POINTER(ob_error))]
ob.ob_delete_device_list.restype = None

# Pipeline functions
ob.ob_create_pipeline_with_device.argtypes = [POINTER(ob_device), POINTER(POINTER(ob_error))]
ob.ob_create_pipeline_with_device.restype = POINTER(ob_pipeline)

ob.ob_delete_pipeline.argtypes = [POINTER(ob_pipeline), POINTER(POINTER(ob_error))]
ob.ob_delete_pipeline.restype = None

ob.ob_pipeline_start_with_config.argtypes = [POINTER(ob_pipeline), POINTER(ob_config), POINTER(POINTER(ob_error))]
ob.ob_pipeline_start_with_config.restype = None

ob.ob_pipeline_stop.argtypes = [POINTER(ob_pipeline), POINTER(POINTER(ob_error))]
ob.ob_pipeline_stop.restype = None

ob.ob_pipeline_wait_for_frameset.argtypes = [POINTER(ob_pipeline), c_uint32, POINTER(POINTER(ob_error))]
ob.ob_pipeline_wait_for_frameset.restype = POINTER(ob_frame)

# Config functions
ob.ob_create_config.argtypes = [POINTER(POINTER(ob_error))]
ob.ob_create_config.restype = POINTER(ob_config)

ob.ob_delete_config.argtypes = [POINTER(ob_config), POINTER(POINTER(ob_error))]
ob.ob_delete_config.restype = None

ob.ob_config_enable_video_stream.argtypes = [
    POINTER(ob_config), c_int, c_int, c_int, c_int, c_int, POINTER(POINTER(ob_error))
]
ob.ob_config_enable_video_stream.restype = None

# Frame functions
ob.ob_delete_frame.argtypes = [POINTER(ob_frame), POINTER(POINTER(ob_error))]
ob.ob_delete_frame.restype = None

ob.ob_frameset_color_frame.argtypes = [POINTER(ob_frame), POINTER(POINTER(ob_error))]
ob.ob_frameset_color_frame.restype = POINTER(ob_frame)

ob.ob_frameset_depth_frame.argtypes = [POINTER(ob_frame), POINTER(POINTER(ob_error))]
ob.ob_frameset_depth_frame.restype = POINTER(ob_frame)

ob.ob_frame_data.argtypes = [POINTER(ob_frame), POINTER(POINTER(ob_error))]
ob.ob_frame_data.restype = c_void_p

ob.ob_frame_data_size.argtypes = [POINTER(ob_frame), POINTER(POINTER(ob_error))]
ob.ob_frame_data_size.restype = c_uint32

ob.ob_video_frame_width.argtypes = [POINTER(ob_frame), POINTER(POINTER(ob_error))]
ob.ob_video_frame_width.restype = c_uint32

ob.ob_video_frame_height.argtypes = [POINTER(ob_frame), POINTER(POINTER(ob_error))]
ob.ob_video_frame_height.restype = c_uint32

ob.ob_frame_format.argtypes = [POINTER(ob_frame), POINTER(POINTER(ob_error))]
ob.ob_frame_format.restype = c_int


# ========== Helper Functions ==========

def check_error(error_ptr):
    """Check for SDK errors and raise exception if needed."""
    if error_ptr:
        err = error_ptr.contents
        msg = err.message.decode('utf-8') if err.message else "Unknown error"
        raise RuntimeError(f"OrbbecSDK Error: {msg}")


# ========== CameraDevice Class ==========

class CameraDevice:
    """
    Singleton managing physical Orbbec camera using C SDK.

    Provides RGB and Depth streams with background capture thread.
    Thread-safe access to latest frames.
    """

    _instance: Optional['CameraDevice'] = None
    _lock = threading.Lock()
    _devices = {}  # Track all camera instances by device_id

    def __init__(self, device_id: int = 0):
        """
        Initialize Orbbec camera device.

        Args:
            device_id: Camera device index (default 0)
        """
        if not HAS_ORBBEC:
            raise ImportError(f"OrbbecSDK library not found at {SDK_LIB_PATH}")

        self.device_id = device_id
        self._context: Optional[POINTER(ob_context)] = None
        self._pipeline: Optional[POINTER(ob_pipeline)] = None
        self._config: Optional[POINTER(ob_config)] = None
        self._device: Optional[POINTER(ob_device)] = None
        self._device_list: Optional[POINTER(ob_device_list)] = None

        # Latest frames
        self._latest_rgb: Optional[np.ndarray] = None
        self._latest_depth: Optional[np.ndarray] = None
        self._frame_lock = threading.RLock()

        # Capture thread
        self._capture_thread: Optional[threading.Thread] = None
        self._running = False

        logger.info(f"CameraDevice {device_id} created")

    @classmethod
    def get_default(cls, device_id: int = 0) -> 'CameraDevice':
        """
        Get or create default camera device (singleton per device_id).

        Args:
            device_id: Camera device index

        Returns:
            CameraDevice instance
        """
        with cls._lock:
            if device_id not in cls._devices:
                instance = cls(device_id=device_id)
                cls._devices[device_id] = instance
                logger.info(f"Created CameraDevice singleton for device {device_id}")
            else:
                logger.debug(f"Reusing existing CameraDevice for device {device_id}")

            return cls._devices[device_id]

    @classmethod
    def cleanup_all(cls):
        """Stop and cleanup all camera devices."""
        with cls._lock:
            for device_id, device in cls._devices.items():
                try:
                    device.stop()
                    logger.info(f"Cleaned up CameraDevice {device_id}")
                except Exception as e:
                    logger.error(f"Error cleaning up CameraDevice {device_id}: {e}")
            cls._devices.clear()

    def start(self, rgb_width: int = 640, rgb_height: int = 480,
              depth_width: int = 640, depth_height: int = 480,
              fps: int = 30):
        """
        Start camera capture.

        Args:
            rgb_width: RGB frame width (default 640)
            rgb_height: RGB frame height (default 480)
            depth_width: Depth frame width (default 640)
            depth_height: Depth frame height (default 480)
            fps: Frame rate (default 30)
        """
        if self._running:
            logger.warning("Camera already running")
            return

        try:
            error = POINTER(ob_error)()

            # Create context
            self._context = ob.ob_create_context(byref(error))
            check_error(error)

            # Query devices
            self._device_list = ob.ob_query_device_list(self._context, byref(error))
            check_error(error)

            count = ob.ob_device_list_device_count(self._device_list, byref(error))
            check_error(error)

            if count == 0:
                raise RuntimeError("No Orbbec devices found")

            if self.device_id >= count:
                raise RuntimeError(
                    f"Device {self.device_id} not found "
                    f"(only {count} device(s) available)"
                )

            # Get device
            self._device = ob.ob_device_list_get_device(
                self._device_list, self.device_id, byref(error)
            )
            check_error(error)

            # Create pipeline
            self._pipeline = ob.ob_create_pipeline_with_device(self._device, byref(error))
            check_error(error)

            # Create config
            self._config = ob.ob_create_config(byref(error))
            check_error(error)

            # Enable RGB stream with default profile (ANY = use device defaults)
            logger.info("Enabling RGB stream with default profile")
            ob.ob_config_enable_video_stream(
                self._config,
                OB_STREAM_COLOR,
                OB_WIDTH_ANY,  # Use device default
                OB_HEIGHT_ANY,
                OB_FPS_ANY,
                OB_FORMAT_ANY,
                byref(error)
            )
            check_error(error)

            # Enable Depth stream with default profile
            logger.info("Enabling Depth stream with default profile")
            ob.ob_config_enable_video_stream(
                self._config,
                OB_STREAM_DEPTH,
                OB_WIDTH_ANY,  # Use device default
                OB_HEIGHT_ANY,
                OB_FPS_ANY,
                OB_FORMAT_ANY,
                byref(error)
            )
            check_error(error)

            # Start pipeline
            ob.ob_pipeline_start_with_config(self._pipeline, self._config, byref(error))
            check_error(error)
            logger.info("Camera pipeline started")

            # Start capture thread
            self._running = True
            self._capture_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True,
                name=f"camera-{self.device_id}"
            )
            self._capture_thread.start()

            logger.info(f"CameraDevice {self.device_id} started")

        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            self._running = False
            self._cleanup_resources()
            raise

    def stop(self):
        """Stop camera capture."""
        if not self._running:
            return

        logger.info(f"Stopping CameraDevice {self.device_id}...")
        self._running = False

        # Wait for capture thread
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)

        # Cleanup resources
        self._cleanup_resources()

        # Clear frames
        with self._frame_lock:
            self._latest_rgb = None
            self._latest_depth = None

        logger.info(f"CameraDevice {self.device_id} stopped")

    def _cleanup_resources(self):
        """Cleanup SDK resources."""
        error = POINTER(ob_error)()

        # Stop pipeline
        if self._pipeline:
            try:
                ob.ob_pipeline_stop(self._pipeline, byref(error))
                ob.ob_delete_pipeline(self._pipeline, byref(error))
            except:
                pass
            self._pipeline = None

        # Delete config
        if self._config:
            try:
                ob.ob_delete_config(self._config, byref(error))
            except:
                pass
            self._config = None

        # Delete device list
        if self._device_list:
            try:
                ob.ob_delete_device_list(self._device_list, byref(error))
            except:
                pass
            self._device_list = None

        # Delete context
        if self._context:
            try:
                ob.ob_delete_context(self._context, byref(error))
            except:
                pass
            self._context = None

    def _capture_loop(self):
        """
        Background capture loop.
        Continuously reads frames from camera and updates latest frames.
        """
        logger.info(f"Capture thread started for device {self.device_id}")

        while self._running:
            try:
                error = POINTER(ob_error)()

                # Wait for frames (timeout 100ms)
                frameset = ob.ob_pipeline_wait_for_frameset(
                    self._pipeline, 100, byref(error)
                )

                if not frameset:
                    continue

                # Process RGB frame
                try:
                    color_frame = ob.ob_frameset_color_frame(frameset, byref(error))
                    if color_frame:
                        width = ob.ob_video_frame_width(color_frame, byref(error))
                        height = ob.ob_video_frame_height(color_frame, byref(error))
                        data_size = ob.ob_frame_data_size(color_frame, byref(error))
                        data_ptr = ob.ob_frame_data(color_frame, byref(error))
                        fmt = ob.ob_frame_format(color_frame, byref(error))

                        # Copy data to buffer
                        buffer = (c_ubyte * data_size).from_address(data_ptr)

                        # Decode based on format
                        if fmt == OB_FORMAT_MJPG:
                            # MJPG format - need to decode JPEG
                            if HAS_CV2:
                                jpeg_data = np.frombuffer(buffer, dtype=np.uint8)
                                rgb_image = cv2.imdecode(jpeg_data, cv2.IMREAD_COLOR)
                                if rgb_image is not None:
                                    # cv2.imdecode returns BGR, convert to RGB
                                    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
                                    with self._frame_lock:
                                        self._latest_rgb = rgb_image.copy()
                            else:
                                logger.debug("MJPG frame received but OpenCV not available for decoding")
                        elif fmt == OB_FORMAT_RGB:
                            # Raw RGB format
                            rgb_image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 3))
                            with self._frame_lock:
                                self._latest_rgb = rgb_image.copy()
                        else:
                            logger.debug(f"Unsupported color format: {fmt}")

                        ob.ob_delete_frame(color_frame, byref(error))
                except Exception as e:
                    logger.debug(f"RGB frame error: {e}")

                # Process Depth frame
                try:
                    depth_frame = ob.ob_frameset_depth_frame(frameset, byref(error))
                    if depth_frame:
                        width = ob.ob_video_frame_width(depth_frame, byref(error))
                        height = ob.ob_video_frame_height(depth_frame, byref(error))
                        data_size = ob.ob_frame_data_size(depth_frame, byref(error))
                        data_ptr = ob.ob_frame_data(depth_frame, byref(error))

                        # Copy data to numpy array (uint16, millimeters)
                        buffer = (c_ubyte * data_size).from_address(data_ptr)
                        depth_image = np.frombuffer(buffer, dtype=np.uint16).reshape((height, width))

                        with self._frame_lock:
                            self._latest_depth = depth_image.copy()

                        ob.ob_delete_frame(depth_frame, byref(error))
                except Exception as e:
                    logger.debug(f"Depth frame error: {e}")

                # Delete frameset
                ob.ob_delete_frame(frameset, byref(error))

            except Exception as e:
                if self._running:
                    logger.error(f"Capture error: {e}")
                time.sleep(0.1)

        logger.info(f"Capture thread stopped for device {self.device_id}")

    def get_latest_rgb(self) -> Optional[np.ndarray]:
        """
        Get latest RGB frame.

        Returns:
            RGB image as numpy array (H, W, 3) uint8, or None if no frame available
        """
        with self._frame_lock:
            return self._latest_rgb.copy() if self._latest_rgb is not None else None

    def get_latest_depth(self) -> Optional[np.ndarray]:
        """
        Get latest depth frame.

        Returns:
            Depth image as numpy array (H, W) uint16 in millimeters, or None
        """
        with self._frame_lock:
            return self._latest_depth.copy() if self._latest_depth is not None else None

    def get_latest_frames(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Get both RGB and depth frames atomically.

        Returns:
            Tuple of (rgb_image, depth_image), either may be None
        """
        with self._frame_lock:
            rgb = self._latest_rgb.copy() if self._latest_rgb is not None else None
            depth = self._latest_depth.copy() if self._latest_depth is not None else None
            return rgb, depth

    @property
    def is_connected(self) -> bool:
        """Check if camera is running."""
        return self._running

    def __repr__(self):
        return f"CameraDevice(device_id={self.device_id}, running={self._running})"


# Auto-cleanup on exit
atexit.register(CameraDevice.cleanup_all)
