#!/usr/bin/env python3
"""
Lesson 1.2: Control Speed - SOLUTION
====================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 1.2: Control Speed!")
    print("=" * 60)
    print()

    # Create a motor with CAN ID 1
    motor = Servo42D(can_id=1)

    # Start the motor
    motor.start()

    print("Starting slow: 20 RPM")
    motor.run(20)
    time.sleep(2)

    print("Speeding up: 60 RPM")
    motor.run(60)
    time.sleep(2)

    print("Slowing down: 30 RPM")
    motor.run(30)
    time.sleep(2)

    print("Reversing: -40 RPM")
    motor.run(-40)
    time.sleep(2)

    print("Stopping motor...")
    motor.stop()

    print()
    print("=" * 60)
    print("Great! You controlled the speed in real-time!")
    print("=" * 60)


if __name__ == "__main__":
    main()
