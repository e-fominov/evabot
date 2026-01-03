#!/usr/bin/env python3
"""
Lesson 3.4: Combine Movements
==============================

Use all 3 degrees of freedom at once!

Instructions:
1. Create robot with mecanum drive
2. Combine forward + strafe (diagonal)
3. Combine forward + rotation (arc)
4. Combine strafe + rotation (sideways arc)
5. Combine ALL THREE! (forward + strafe + rotation)

Fill in the blanks marked with # TODO
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

    # TODO: Move diagonally forward-left
    # Hint: robot.drive.move(vx=???, vy=???)


    time.sleep(4)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 2: Forward Arc (Forward + Rotate CCW)")
    print("vx=0.2 m/s forward, vtheta=0.4 rad/s CCW")

    # TODO: Create forward arc
    # Hint: robot.drive.move(vx=???, vtheta=???)


    time.sleep(5)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 3: Sideways Arc (Strafe Right + Rotate CW)")
    print("vy=-0.15 m/s right, vtheta=-0.4 rad/s CW")

    # TODO: Create sideways arc
    # Hint: vy negative = right, vtheta negative = CW


    time.sleep(5)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Test 4: FULL OMNI (Forward + Strafe + Rotate)!")
    print("vx=0.15 forward, vy=0.1 left, vtheta=0.3 CCW")
    print("(Complex 3D motion!)")

    # TODO: Combine all three motions
    # Hint: robot.drive.move(vx=???, vy=???, vtheta=???)


    time.sleep(6)
    robot.drive.halt()
    time.sleep(1)

    print()
    print("Bonus: Circle while facing forward!")
    print("vx=0.25 forward, vtheta=0.25 CCW")

    # TODO: Drive in a circle while facing forward
    # Hint: For radius r, use vx and vtheta = vx/r


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
