#!/usr/bin/env python3
"""
Lesson 1.3: Start and Stop - SOLUTION
=====================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 1.3: Start and Stop!")
    print("=" * 60)
    print()

    # Create a motor with CAN ID 1
    motor = Servo42D(can_id=1)

    print("Enabling motor (shaft will lock)...")
    print(">>> Try to turn the motor shaft by hand!")
    input("Press Enter when ready to continue...")

    # Start (enable) the motor
    motor.start()

    print()
    print("Motor is now ENABLED (shaft locked)")
    print(">>> Try turning the shaft - it should be hard!")
    input("Press Enter to continue...")

    print()
    print("Running motor at 40 RPM...")
    motor.run(40)
    time.sleep(2)

    print()
    print("Using hold() - motor stops but stays locked...")
    motor.hold()
    print(">>> Try turning the shaft - still hard!")
    input("Press Enter to continue...")

    print()
    print("Waiting 2 seconds while held...")
    time.sleep(2)

    print()
    print("Using disable() - releasing shaft...")
    motor.disable()
    print(">>> Try turning the shaft - now it's easy!")
    input("Press Enter to continue...")

    print()
    print("Running motor again at 30 RPM...")
    motor.start()
    motor.run(30)
    time.sleep(2)

    print()
    print("Using stop() - holds briefly, then disables...")
    motor.stop()

    print()
    print("Motor is now STOPPED (shaft free)")
    print(">>> Try turning the shaft - it should be easy!")
    input("Press Enter to finish...")

    print()
    print("=" * 60)
    print("Great! You understand hold(), disable(), and stop()!")
    print("=" * 60)


if __name__ == "__main__":
    main()
