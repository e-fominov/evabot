#!/usr/bin/env python3
"""
Lesson 1.3: Start and Stop
==========================

Understand motor enable/disable and safe shutdown.

Instructions:
1. Create a motor
2. Enable it (start) - try turning shaft by hand!
3. Run the motor
4. Stop the motor - try turning shaft again!
5. Notice the difference!

Fill in the blanks marked with # TODO
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 1.3: Start and Stop!")
    print("=" * 60)
    print()

    # TODO: Create a motor with CAN ID 1


    print("Enabling motor (shaft will lock)...")
    print(">>> Try to turn the motor shaft by hand!")
    input("Press Enter when ready to continue...")

    # TODO: Start (enable) the motor
    # Hint: motor.start()


    print()
    print("Motor is now ENABLED (shaft locked)")
    print(">>> Try turning the shaft - it should be hard!")
    input("Press Enter to continue...")

    print()
    print("Running motor at 40 RPM...")

    # TODO: Run the motor at 40 RPM


    time.sleep(3)

    print()
    print("Stopping motor...")

    # TODO: Stop the motor (disables and releases shaft)


    print()
    print("Motor is now DISABLED (shaft free)")
    print(">>> Try turning the shaft - it should be easy!")
    input("Press Enter to finish...")

    print()
    print("=" * 60)
    print("Great! You understand motor enable/disable!")
    print("=" * 60)


if __name__ == "__main__":
    main()
