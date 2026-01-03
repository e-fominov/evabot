#!/usr/bin/env python3
"""
Lesson 3.1: Forward and Backward
=================================

Drive your robot using the MecanumDrive system!

Instructions:
1. Import Robot and MecanumDrive
2. Create a robot with mecanum drive
3. Start the robot
4. Drive forward
5. Drive backward
6. Stop the robot

Fill in the blanks marked with # TODO
"""

import time

# TODO: Import Robot and MecanumDrive
# Hint: from evabot import Robot, MecanumDrive


def main():
    print("=" * 60)
    print("Lesson 3.1: Forward and Backward!")
    print("=" * 60)
    print()

    # TODO: Create a Robot
    # Hint: robot = Robot()


    # TODO: Add MecanumDrive to robot
    # Hint: robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)


    # TODO: Start the robot (this starts all motors)
    # Hint: robot.start()


    print()
    print("Driving forward at 0.2 m/s for 3 seconds...")

    # TODO: Drive forward at 0.2 m/s
    # Hint: robot.drive.forward(???)


    time.sleep(3)

    print("Stopping...")

    # TODO: Stop movement (halt)
    # Hint: robot.drive.halt()


    time.sleep(1)

    print()
    print("Driving backward at 0.2 m/s for 3 seconds...")

    # TODO: Drive backward at 0.2 m/s
    # Hint: robot.drive.backward(???)


    time.sleep(3)

    print("Stopping...")

    # TODO: Halt movement


    time.sleep(1)

    print()
    print("Shutting down robot...")

    # TODO: Stop the robot (this stops all motors)
    # Hint: robot.stop()


    print()
    print("=" * 60)
    print("Great! Your robot drove forward and backward!")
    print("=" * 60)


if __name__ == "__main__":
    main()
