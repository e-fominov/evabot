#!/usr/bin/env python3
"""
Lesson 2.2: Four Motors
=======================

Control all four motors for a robot base!

Motor layout:
    FRONT
  FL    FR     FL = CAN ID 4
               FR = CAN ID 2
  BL    BR     BL = CAN ID 3
    BACK       BR = CAN ID 1

Instructions:
1. Create four motor objects (CAN IDs: FL=4, FR=2, BL=3, BR=1)
2. Start all motors
3. Control them in groups (all, left/right, front/back)
4. Stop all motors

Fill in the blanks marked with # TODO
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 2.2: Four Motors!")
    print("=" * 60)
    print()

    print("Creating motors...")

    # TODO: Create four motors
    # Hint: fl = Servo42D(can_id=4), fr = Servo42D(can_id=2), etc.





    print("Starting all motors...")

    # TODO: Start all four motors
    # Hint: fl.start(), fr.start(), etc.





    print()
    print("Test 1: All motors forward at 30 RPM")

    # TODO: Run all motors at 30 RPM





    time.sleep(3)

    print()
    print("Test 2: Left side 40 RPM, Right side 20 RPM")

    # TODO: Run FL and BL at 40 RPM (left side)


    # TODO: Run FR and BR at 20 RPM (right side)


    time.sleep(3)

    print()
    print("Test 3: Front forward 30 RPM, Back backward -30 RPM")

    # TODO: Run FL and FR at +30 RPM (front)


    # TODO: Run BL and BR at -30 RPM (back)


    time.sleep(3)

    print()
    print("Stopping all motors...")

    # TODO: Stop all four motors





    print()
    print("=" * 60)
    print("Excellent! You controlled four motors!")
    print("=" * 60)


if __name__ == "__main__":
    main()
