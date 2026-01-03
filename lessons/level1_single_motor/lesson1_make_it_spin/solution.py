#!/usr/bin/env python3
"""
Lesson 1.1: Make It Spin - SOLUTION
====================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 1.1: Make It Spin!")
    print("=" * 60)
    print()

    # Create a motor with CAN ID 1
    motor = Servo42D(can_id=1)

    # Start the motor (connects to CAN bus and enables it)
    motor.start()

    print("Starting motor at 30 RPM...")

    # Make the motor run at 30 RPM
    motor.run(30)

    print("Motor is spinning!")
    print("Waiting 3 seconds...")

    # Wait for 3 seconds
    time.sleep(3)

    print("Stopping motor...")

    # Stop the motor (disables it and releases shaft)
    motor.stop()

    print()
    print("=" * 60)
    print("Great job! The motor spun and stopped safely.")
    print("=" * 60)


if __name__ == "__main__":
    main()
