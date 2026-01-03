#!/usr/bin/env python3
"""
Lesson 2.2: Four Motors - SOLUTION
==================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 2.2: Four Motors!")
    print("=" * 60)
    print()

    print("Creating motors...")
    # Create four motors (FL=4, FR=2, BL=3, BR=1)
    fl = Servo42D(can_id=4)
    fr = Servo42D(can_id=2)
    bl = Servo42D(can_id=3)
    br = Servo42D(can_id=1)

    print("Starting all motors...")
    fl.start()
    fr.start()
    bl.start()
    br.start()

    print()
    print("Test 1: All motors forward at 30 RPM")
    fl.run(30)
    fr.run(30)
    bl.run(30)
    br.run(30)
    time.sleep(3)

    print()
    print("Test 2: Left side 40 RPM, Right side 20 RPM")
    fl.run(40)  # Left side
    bl.run(40)
    fr.run(20)  # Right side
    br.run(20)
    time.sleep(3)

    print()
    print("Test 3: Front forward 30 RPM, Back backward -30 RPM")
    fl.run(30)  # Front
    fr.run(30)
    bl.run(-30)  # Back
    br.run(-30)
    time.sleep(3)

    print()
    print("Stopping all motors...")
    fl.stop()
    fr.stop()
    bl.stop()
    br.stop()

    print()
    print("=" * 60)
    print("Excellent! You controlled four motors!")
    print("=" * 60)


if __name__ == "__main__":
    main()
