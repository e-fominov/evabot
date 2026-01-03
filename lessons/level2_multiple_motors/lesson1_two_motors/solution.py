#!/usr/bin/env python3
"""
Lesson 2.1: Two Motors Together - SOLUTION
==========================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 2.1: Two Motors Together!")
    print("=" * 60)
    print()

    # Create two motors with CAN ID 1 and 2
    motor1 = Servo42D(can_id=1)
    motor2 = Servo42D(can_id=2)

    print("Starting both motors...")
    motor1.start()
    motor2.start()

    print()
    print("Test 1: Both motors forward at 30 RPM (synchronized)")
    motor1.run(30)
    motor2.run(30)
    time.sleep(3)

    print()
    print("Test 2: Different speeds (Motor1=40, Motor2=20)")
    motor1.run(40)
    motor2.run(20)
    time.sleep(3)

    print()
    print("Test 3: Opposite directions (Motor1=+30, Motor2=-30)")
    motor1.run(30)
    motor2.run(-30)
    time.sleep(3)

    print()
    print("Stopping both motors...")
    motor1.stop()
    motor2.stop()

    print()
    print("=" * 60)
    print("Great! You controlled two motors together!")
    print("=" * 60)


if __name__ == "__main__":
    main()
