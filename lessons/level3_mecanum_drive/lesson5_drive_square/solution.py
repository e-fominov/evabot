#!/usr/bin/env python3
"""
Lesson 3.5: Drive a Square - SOLUTION
=====================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot import Robot, MecanumDrive

# Constants
VELOCITY = 0.2  # m/s
SIDE_LENGTH = 1.0  # meters
SIDE_TIME = SIDE_LENGTH / VELOCITY  # 5 seconds


def main():
    print("=" * 60)
    print("Lesson 3.5: Drive a Square!")
    print("=" * 60)
    print()
    print(f"Target: {SIDE_LENGTH}m × {SIDE_LENGTH}m square")
    print(f"Velocity: {VELOCITY} m/s")
    print(f"Time per side: {SIDE_TIME} seconds")
    print()

    # Create robot with mecanum drive
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.start()

    input("Press Enter to start driving the square...")
    print()

    # Side 1: Forward
    print(f"Side 1: Forward {SIDE_LENGTH}m ({SIDE_TIME}s)")
    robot.drive.forward(VELOCITY)
    time.sleep(SIDE_TIME)
    robot.drive.halt()
    time.sleep(0.5)

    # Side 2: Strafe Left
    print(f"Side 2: Strafe Left {SIDE_LENGTH}m ({SIDE_TIME}s)")
    robot.drive.strafe_left(VELOCITY)
    time.sleep(SIDE_TIME)
    robot.drive.halt()
    time.sleep(0.5)

    # Side 3: Backward
    print(f"Side 3: Backward {SIDE_LENGTH}m ({SIDE_TIME}s)")
    robot.drive.backward(VELOCITY)
    time.sleep(SIDE_TIME)
    robot.drive.halt()
    time.sleep(0.5)

    # Side 4: Strafe Right
    print(f"Side 4: Strafe Right {SIDE_LENGTH}m ({SIDE_TIME}s)")
    robot.drive.strafe_right(VELOCITY)
    time.sleep(SIDE_TIME)
    robot.drive.halt()

    print()
    print("Square complete!")
    print("Check if robot returned to start position.")
    print()

    # Show final position
    print(f"Final position: {robot.odom.pose}")
    print(f"Expected: near (0, 0, 0)")
    print()

    print("Shutting down...")
    robot.stop()

    print()
    print("=" * 60)
    print("Great! You drove a square path!")
    print("=" * 60)


if __name__ == "__main__":
    main()
