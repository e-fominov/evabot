#!/usr/bin/env python3
"""
Sensor components for robots.
"""

from .lidar import RPLidarC1
from .camera import OrbbecCamera

__all__ = [
    "RPLidarC1",
    "OrbbecCamera",
]
