#!/usr/bin/env python3
"""
Internal state management (thread-safe).
Not directly exposed to users - accessed through component properties.
"""

import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import math


@dataclass
class Pose:
    """Robot pose (position + orientation) in a specific frame"""
    x: float = 0.0      # meters
    y: float = 0.0      # meters
    theta: float = 0.0  # radians

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'x': self.x,
            'y': self.y,
            'theta': self.theta
        }

    def __repr__(self):
        theta_deg = math.degrees(self.theta)
        return f"Pose(x={self.x:.3f}m, y={self.y:.3f}m, θ={theta_deg:.1f}°)"


@dataclass
class Velocity:
    """Robot velocity (linear + angular)"""
    vx: float = 0.0      # m/s forward
    vy: float = 0.0      # m/s left (for mecanum)
    vtheta: float = 0.0  # rad/s counter-clockwise


class OdomState:
    """
    Odometry state (thread-safe).

    Internal state for odometry frame. Accessed through Odometry component.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._pose = Pose()
        self._velocity = Velocity()

    @property
    def x(self) -> float:
        """X position in meters (odometry frame)"""
        with self._lock:
            return self._pose.x

    @x.setter
    def x(self, value: float):
        with self._lock:
            self._pose.x = value

    @property
    def y(self) -> float:
        """Y position in meters (odometry frame)"""
        with self._lock:
            return self._pose.y

    @y.setter
    def y(self, value: float):
        with self._lock:
            self._pose.y = value

    @property
    def theta(self) -> float:
        """Orientation in radians (odometry frame)"""
        with self._lock:
            return self._pose.theta

    @theta.setter
    def theta(self, value: float):
        with self._lock:
            self._pose.theta = value

    @property
    def pose(self) -> Pose:
        """Get a copy of the current pose"""
        with self._lock:
            return Pose(
                x=self._pose.x,
                y=self._pose.y,
                theta=self._pose.theta
            )

    def set_pose(self, x: float, y: float, theta: float):
        """Set pose atomically"""
        with self._lock:
            self._pose.x = x
            self._pose.y = y
            self._pose.theta = theta

    @property
    def velocity(self) -> Velocity:
        """Get a copy of current velocity"""
        with self._lock:
            return Velocity(
                vx=self._velocity.vx,
                vy=self._velocity.vy,
                vtheta=self._velocity.vtheta
            )

    def set_velocity(self, vx: float, vy: float, vtheta: float):
        """Set velocity atomically"""
        with self._lock:
            self._velocity.vx = vx
            self._velocity.vy = vy
            self._velocity.vtheta = vtheta


class LidarState:
    """
    Lidar sensor state (thread-safe).

    Internal state for lidar. Accessed through Lidar component.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._scan: Dict[int, float] = {}  # {angle_deg: distance_m}

    def update_scan(self, scan: Dict[int, float]):
        """Update full scan atomically"""
        with self._lock:
            self._scan = dict(scan)

    def get_scan(self) -> Dict[int, float]:
        """Get copy of scan data"""
        with self._lock:
            return dict(self._scan)

    def get_distance(self, angle_deg: int) -> float:
        """Get distance at specific angle in meters"""
        with self._lock:
            return self._scan.get(angle_deg % 360, float('inf'))

    @property
    def front(self) -> float:
        """Distance in front (0°) in meters"""
        return self.get_distance(0)

    @property
    def back(self) -> float:
        """Distance in back (180°) in meters"""
        return self.get_distance(180)

    @property
    def left(self) -> float:
        """Distance to left (90°) in meters"""
        return self.get_distance(90)

    @property
    def right(self) -> float:
        """Distance to right (270°) in meters"""
        return self.get_distance(270)


class CameraState:
    """
    Camera sensor state (thread-safe).

    Internal state for camera. Accessed through Camera component.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._frame: Optional[Any] = None  # RGB image (numpy array)
        self._depth: Optional[Any] = None  # Depth image (numpy array)
        self._detections: Dict[str, tuple] = {}  # {color: (x, y, detected)}

    def update_frame(self, frame: Any):
        """Update RGB frame"""
        with self._lock:
            self._frame = frame

    def update_depth(self, depth: Any):
        """Update depth frame"""
        with self._lock:
            self._depth = depth

    def update_detection(self, color: str, detected: bool, center: tuple = (0, 0)):
        """Update color detection result"""
        with self._lock:
            self._detections[color] = (center[0], center[1], detected)

    @property
    def image(self) -> Optional[Any]:
        """Get latest RGB frame"""
        with self._lock:
            return self._frame

    @property
    def depth(self) -> Optional[Any]:
        """Get latest depth frame"""
        with self._lock:
            return self._depth

    def get_detection(self, color: str) -> tuple:
        """Get detection result: (x, y, detected)"""
        with self._lock:
            return self._detections.get(color, (0, 0, False))

    def depth_at(self, x: int, y: int) -> float:
        """Get depth at pixel (x, y) in meters"""
        with self._lock:
            if self._depth is None:
                return float('inf')
            try:
                # Assuming depth is numpy array
                return float(self._depth[y, x])
            except (IndexError, TypeError):
                return float('inf')


class RobotState:
    """
    Internal robot state container (thread-safe).

    Not exposed directly to users. Components access this internally
    and expose clean interfaces (robot.odom.x, robot.lidar.front, etc.)
    """

    def __init__(self):
        # Frame-specific states
        self.odom = OdomState()      # Odometry frame
        # self.map will be added in Phase 7 for SLAM

        # Sensor states
        self.lidar = LidarState()
        self.camera = CameraState()
