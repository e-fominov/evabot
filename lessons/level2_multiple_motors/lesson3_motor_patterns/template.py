#!/usr/bin/env python3
"""
Lesson 2.3: Motor Patterns
==========================

Create beautiful coordinated motor patterns!

Motor layout:
    FRONT
  FL    FR     FL = CAN ID 4
               FR = CAN ID 2
  BL    BR     BL = CAN ID 3
    BACK       BR = CAN ID 1

Instructions:
1. Create and start four motors
2. Create a wave pattern (sequential start)
3. Create a pulse pattern (synchronized speed changes)
4. Create a spin pattern (rotational effect)
5. Create your own custom pattern!

Fill in the blanks marked with # TODO
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

    # TODO: Start FL at 40 RPM

    time.sleep(0.5)

    # TODO: Start FR at 40 RPM

    time.sleep(0.5)

    # TODO: Start BR at 40 RPM

    time.sleep(0.5)

    # TODO: Start BL at 40 RPM

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

        # TODO: Set all motors to current speed (use the 'speed' variable)




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

    # TODO: FL and BR forward at 40 RPM


    # TODO: FR and BL backward at -40 RPM


    time.sleep(3)

    # TODO: Switch directions - FL and BR backward


    # TODO: FR and BL forward


    time.sleep(3)

    # ========== Your Custom Pattern! ==========
    print("Pattern 4: Your Custom Pattern!")
    print("(Add your own creative pattern here!)")
    print()

    # TODO: Create your own pattern!
    # Ideas: alternating, spiral, random, music-like, etc.
    # Be creative!

    time.sleep(3)

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
