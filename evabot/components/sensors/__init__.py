#!/usr/bin/env python3
"""
Sensor components for robots.
"""

from .lidar import RPLidarC1

__all__ = [
    "RPLidarC1",
    "Camera",
]


def __getattr__(name):
    if name == "Camera":
        from .camera import Camera
        return Camera
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
