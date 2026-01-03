#!/usr/bin/env python3
"""
Lesson 2.1: Two Motors Together
===============================

Control two motors at the same time!

Instructions:
1. Create TWO motor objects (CAN ID 1 and 2)
2. Start both motors
3. Run them together at same speed
4. Run them at different speeds
5. Run them in opposite directions
6. Stop both motors

Fill in the blanks marked with # TODO
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 2.1: Two Motors Together!")
    print("=" * 60)
    print()

    # TODO: Create first motor with CAN ID 1
    # Hint: motor1 = Servo42D(can_id=???)


    # TODO: Create second motor with CAN ID 2


    print("Starting both motors...")

    # TODO: Start motor 1


    # TODO: Start motor 2


    print()
    print("Test 1: Both motors forward at 30 RPM (synchronized)")

    # TODO: Run motor1 at 30 RPM


    # TODO: Run motor2 at 30 RPM


    time.sleep(3)

    print()
    print("Test 2: Different speeds (Motor1=40, Motor2=20)")

    # TODO: Run motor1 at 40 RPM


    # TODO: Run motor2 at 20 RPM


    time.sleep(3)

    print()
    print("Test 3: Opposite directions (Motor1=+30, Motor2=-30)")

    # TODO: Run motor1 at +30 RPM (forward)


    # TODO: Run motor2 at -30 RPM (backward)


    time.sleep(3)

    print()
    print("Stopping both motors...")

    # TODO: Stop motor1


    # TODO: Stop motor2


    print()
    print("=" * 60)
    print("Great! You controlled two motors together!")
    print("=" * 60)


if __name__ == "__main__":
    main()
