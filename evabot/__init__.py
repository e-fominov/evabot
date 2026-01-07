#!/usr/bin/env python3
"""
EvaBot - Simple robotics library for progressive learning.

Start with a single motor, progress to autonomous robots with sensors.

Usage:
    from evabot import Robot, MecanumDrive

    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)

    # Access data through clear component interfaces
    robot.odom.x         # meters (odometry frame)
    robot.lidar.front    # meters
    robot.camera.image   # RGB image

    robot.start()
"""

__version__ = "0.1.0"

# Main classes
from .robot import Robot
from .components import MecanumDrive, Servo42D, RPLidarC1

# Re-export commonly used items
__all__ = [
    "Robot",
    "MecanumDrive",
    "Servo42D",
    "RPLidarC1",
    "__version__",
]
