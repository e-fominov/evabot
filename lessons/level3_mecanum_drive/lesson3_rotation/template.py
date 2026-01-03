#!/usr/bin/env python3
"""
Lesson 3.3: Rotation
====================

Spin your robot in place and create arcs!

Instructions:
1. Create robot with mecanum drive
2. Rotate counter-clockwise (CCW)
3. Rotate clockwise (CW)
4. Create arc motion (forward + rotation)

Fill in the blanks marked with # TODO
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

    # TODO: Rotate counter-clockwise at 0.5 rad/s
    # Hint: robot.drive.rotate_ccw(???)


    time.sleep(4)  # 4 seconds ≈ 115° rotation
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 2: Rotate CW (clockwise) at 0.5 rad/s")
    print("(Robot should spin RIGHT in place)")

    # TODO: Rotate clockwise at 0.5 rad/s
    # Hint: robot.drive.rotate_cw(???)


    time.sleep(4)  # 4 seconds ≈ 115° rotation
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 3: Arc motion - Forward 0.2 m/s + CCW 0.3 rad/s")
    print("(Robot should move in a curved path)")

    # TODO: Combine forward and rotation
    # Hint: robot.drive.move(vx=???, vtheta=???)
    # vx = forward/backward, vtheta = rotation


    time.sleep(5)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 4: Arc motion - Strafe right + CW rotation")
    print("(Creates sideways arc!)")

    # TODO: Combine strafe right and clockwise rotation
    # Hint: vy negative = right, vtheta negative = clockwise


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
