#!/usr/bin/env python3
"""
Lesson 3.1: Forward and Backward - SOLUTION
===========================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot import Robot, MecanumDrive


def main():
    print("=" * 60)
    print("Lesson 3.1: Forward and Backward!")
    print("=" * 60)
    print()

    # Create a robot
    robot = Robot()

    # Add mecanum drive (FL=4, FR=2, BL=3, BR=1)
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)

    # Start the robot
    robot.start()

    print()
    print("Driving forward at 0.2 m/s for 3 seconds...")
    robot.drive.forward(0.2)
    time.sleep(3)

    print("Stopping...")
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Driving backward at 0.2 m/s for 3 seconds...")
    robot.drive.backward(0.2)
    time.sleep(3)

    print("Stopping...")
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Shutting down robot...")
    robot.stop()

    print()
    print("=" * 60)
    print("Great! Your robot drove forward and backward!")
    print("=" * 60)


if __name__ == "__main__":
    main()
