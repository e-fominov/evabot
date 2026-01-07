#!/usr/bin/env python3
"""
Hardware layer - singleton managers for physical devices.

These are shared across all Robot instances to prevent conflicts
when accessing hardware resources like CAN bus, cameras, etc.
"""

from .can_bus import CanBus
from .lidar_device import LidarDevice
# from .camera_device import CameraDevice  # Temporarily disabled

__all__ = [
    "CanBus",
    "LidarDevice",
    # "CameraDevice",  # Temporarily disabled
]
