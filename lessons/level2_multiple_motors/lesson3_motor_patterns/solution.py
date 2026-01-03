#!/usr/bin/env python3
"""
Lesson 2.3: Motor Patterns - SOLUTION
=====================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 2.3: Motor Patterns!")
    print("=" * 60)
    print()

    # Create motors
    fl = Servo42D(can_id=4)
    fr = Servo42D(can_id=2)
    bl = Servo42D(can_id=3)
    br = Servo42D(can_id=1)

    # Start all motors
    fl.start()
    fr.start()
    bl.start()
    br.start()

    # ========== Pattern 1: Wave ==========
    print()
    print("Pattern 1: Wave (motors start one by one)")
    print()

    fl.run(40)
    time.sleep(0.5)
    fr.run(40)
    time.sleep(0.5)
    br.run(40)
    time.sleep(0.5)
    bl.run(40)
    time.sleep(1.5)

    # Stop all
    fl.run(0)
    fr.run(0)
    bl.run(0)
    br.run(0)
    time.sleep(1)

    # ========== Pattern 2: Pulse ==========
    print("Pattern 2: Pulse (all motors speed up and slow down)")
    print()

    speeds = [20, 30, 40, 50, 60, 50, 40, 30, 20]

    for speed in speeds:
        print(f"  All motors: {speed} RPM")
        fl.run(speed)
        fr.run(speed)
        bl.run(speed)
        br.run(speed)
        time.sleep(0.5)

    # Stop all
    fl.run(0)
    fr.run(0)
    bl.run(0)
    br.run(0)
    time.sleep(1)

    # ========== Pattern 3: Spin ==========
    print("Pattern 3: Spin (diagonal motors create rotation)")
    print()

    # Diagonal 1 forward, Diagonal 2 backward
    fl.run(40)
    br.run(40)
    fr.run(-40)
    bl.run(-40)
    time.sleep(3)

    # Switch directions
    fl.run(-40)
    br.run(-40)
    fr.run(40)
    bl.run(40)
    time.sleep(3)

    # ========== Custom Pattern: Alternating Sides ==========
    print("Pattern 4: Alternating Sides (left-right-left-right)")
    print()

    for _ in range(4):
        # Left side on
        fl.run(50)
        bl.run(50)
        fr.run(0)
        br.run(0)
        time.sleep(0.5)

        # Right side on
        fl.run(0)
        bl.run(0)
        fr.run(50)
        br.run(50)
        time.sleep(0.5)

    # Stop all motors
    print()
    print("Stopping all motors...")
    fl.stop()
    fr.stop()
    bl.stop()
    br.stop()

    print()
    print("=" * 60)
    print("Amazing! You created motor choreography!")
    print("=" * 60)


if __name__ == "__main__":
    main()
