#!/usr/bin/env python3
"""
Lesson 3.3: Rotation - SOLUTION
================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot import Robot, MecanumDrive


def main():
    print("=" * 60)
    print("Lesson 3.3: Rotation!")
    print("=" * 60)
    print()

    # Create robot with mecanum drive
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.start()

    print()
    print("Test 1: Rotate CCW (counter-clockwise) at 0.5 rad/s")
    print("(Robot should spin LEFT in place)")
    robot.drive.rotate_ccw(0.5)
    time.sleep(4)  # 4 seconds ≈ 115° rotation
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 2: Rotate CW (clockwise) at 0.5 rad/s")
    print("(Robot should spin RIGHT in place)")
    robot.drive.rotate_cw(0.5)
    time.sleep(4)  # 4 seconds ≈ 115° rotation
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 3: Arc motion - Forward 0.2 m/s + CCW 0.3 rad/s")
    print("(Robot should move in a curved path)")
    robot.drive.move(vx=0.2, vtheta=0.3)
    time.sleep(5)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 4: Arc motion - Strafe right + CW rotation")
    print("(Creates sideways arc!)")
    robot.drive.move(vy=-0.15, vtheta=-0.3)  # vy negative = right, vtheta negative = CW
    time.sleep(5)
    robot.drive.halt()

    print()
    print("Shutting down...")
    robot.stop()

    print()
    print("=" * 60)
    print("Excellent! You mastered rotation!")
    print("=" * 60)


if __name__ == "__main__":
    main()
