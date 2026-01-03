#!/usr/bin/env python3
"""
Lesson 3.4: Combine Movements - SOLUTION
=========================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot import Robot, MecanumDrive


def main():
    print("=" * 60)
    print("Lesson 3.4: Combine Movements!")
    print("=" * 60)
    print()

    # Create robot with mecanum drive
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.start()

    print()
    print("Test 1: Diagonal (Forward + Strafe Left)")
    print("vx=0.2 m/s forward, vy=0.15 m/s left")
    robot.drive.move(vx=0.2, vy=0.15)
    time.sleep(4)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 2: Forward Arc (Forward + Rotate CCW)")
    print("vx=0.2 m/s forward, vtheta=0.4 rad/s CCW")
    robot.drive.move(vx=0.2, vtheta=0.4)
    time.sleep(5)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 3: Sideways Arc (Strafe Right + Rotate CW)")
    print("vy=-0.15 m/s right, vtheta=-0.4 rad/s CW")
    robot.drive.move(vy=-0.15, vtheta=-0.4)
    time.sleep(5)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 4: FULL OMNI (Forward + Strafe + Rotate)!")
    print("vx=0.15 forward, vy=0.1 left, vtheta=0.3 CCW")
    print("(Complex 3D motion!)")
    robot.drive.move(vx=0.15, vy=0.1, vtheta=0.3)
    time.sleep(6)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Bonus: Circle while facing forward!")
    print("vx=0.25 forward, vtheta=0.25 CCW")
    robot.drive.move(vx=0.25, vtheta=0.25)
    time.sleep(8)
    robot.drive.halt()

    print()
    print("Shutting down...")
    robot.stop()

    print()
    print("=" * 60)
    print("WOW! You mastered omnidirectional control!")
    print("=" * 60)


if __name__ == "__main__":
    main()
