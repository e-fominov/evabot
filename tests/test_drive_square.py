#!/usr/bin/env python3
"""Test mecanum drive: 30cm in each direction + rotations."""
import time
import math
from evabot.robot import Robot
from evabot.components.drive.mecanum import MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1, pattern='X')
robot.start()

DIST = 0.30  # meters
SPEED = 0.15  # m/s
PAUSE = 1.0  # seconds between moves

moves = [
    ("Forward 30cm",  dict(dx=DIST)),
    ("Right 30cm",    dict(dy=-DIST)),
    ("Back 30cm",     dict(dx=-DIST)),
    ("Left 30cm",     dict(dy=DIST)),
    ("Rotate CW 90°", dict(dtheta=-math.pi/2)),
    ("Rotate CCW 90°", dict(dtheta=math.pi/2)),
]

try:
    robot.drive.zero_position()
    time.sleep(0.5)

    for name, kwargs in moves:
        pose = robot.odom.pose
        print(f"\n--- {name} ---")
        print(f"  Before: x={pose.x:.3f} y={pose.y:.3f} theta={math.degrees(pose.theta):.1f}°")

        robot.drive.move_by(**kwargs, speed=SPEED)

        pose = robot.odom.pose
        print(f"  After:  x={pose.x:.3f} y={pose.y:.3f} theta={math.degrees(pose.theta):.1f}°")
        time.sleep(PAUSE)

    pose = robot.odom.pose
    print(f"\n{'='*40}")
    print(f"Final: x={pose.x:.3f} y={pose.y:.3f} theta={math.degrees(pose.theta):.1f}°")
    print(f"Expected: ~(0, 0, 0°)")

finally:
    robot.stop()
    print("Done.")
