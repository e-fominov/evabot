#!/usr/bin/env python3
"""
Lesson 3.2: Strafe (Sideways) - SOLUTION
========================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot import Robot, MecanumDrive


def main():
    print("=" * 60)
    print("Lesson 3.2: Strafe (Sideways)!")
    print("=" * 60)
    print()

    # Create robot with mecanum drive
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.start()

    print()
    print("Test 1: Strafe LEFT at 0.2 m/s for 3 seconds")
    print("(Robot should move left without turning!)")
    robot.drive.strafe_left(0.2)
    time.sleep(3)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 2: Strafe RIGHT at 0.2 m/s for 3 seconds")
    print("(Robot should move right without turning!)")
    robot.drive.strafe_right(0.2)
    time.sleep(3)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 3: Diagonal - Forward + Right at 0.15 m/s each")
    print("(Robot should move diagonally forward-right!)")
    robot.drive.move(vx=0.15, vy=-0.15)  # vy negative = right
    time.sleep(3)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 4: Diagonal - Backward + Left at 0.15 m/s each")
    robot.drive.move(vx=-0.15, vy=0.15)  # vx negative = backward, vy positive = left
    time.sleep(3)
    robot.drive.halt()

    print()
    print("Shutting down...")
    robot.stop()

    print()
    print("=" * 60)
    print("Amazing! You mastered omnidirectional movement!")
    print("=" * 60)


if __name__ == "__main__":
    main()
