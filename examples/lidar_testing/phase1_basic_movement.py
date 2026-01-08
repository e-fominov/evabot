#!/usr/bin/env python3
"""
Phase 1: Basic Mecanum Movement Test

Tests basic mecanum wheel movement in all directions:
- Forward/backward
- Left/right strafe
- Rotation

Motor Configuration (verified):
- FL=3, FR=4, BL=1, BR=2
- Pattern: X (FL\\ FR/ BL/ BR\\)
- All motors are identical: rotate CCW when viewed from wheel side
- Right-side motors (FR, BR) are negated in MecanumDrive.move() to account
  for physical mirroring (mounted on opposite side of robot)

Usage:
    robot run examples/lidar_testing/phase1_basic_movement.py

Result: ✓ All movement directions verified correct
"""

import time
from evabot import Robot, MecanumDrive

def main():
    print("=" * 70)
    print("Phase 1: Basic Mecanum Movement Test")
    print("=" * 70)
    print()
    print("This test will move the robot in all directions to verify")
    print("that mecanum wheels are working correctly.")
    print()
    print("Make sure robot has at least 30cm clearance in all directions!")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)
    print()

    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
    robot.start()

    # Test sequence
    tests = [
        ("Forward", 0.2, 0, 0),
        ("Backward", -0.2, 0, 0),
        ("Strafe Right", 0, -0.2, 0),
        ("Strafe Left", 0, 0.2, 0),
        ("Rotate CW", 0, 0, 0.5),
        ("Rotate CCW", 0, 0, -0.5),
    ]

    for name, vx, vy, vtheta in tests:
        print(f"Test: {name}")
        print(f"  Moving: vx={vx}, vy={vy}, vtheta={vtheta}")

        robot.drive.move(vx=vx, vy=vy, vtheta=vtheta)
        time.sleep(1.0)

        robot.drive.halt()
        print(f"  Stopped. Waiting 2 seconds...")
        time.sleep(2.0)
        print()

    robot.stop()

    print("=" * 70)
    print("Phase 1 Complete!")
    print("=" * 70)
    print()
    print("Verify that robot:")
    print("  ✓ Moved forward and backward")
    print("  ✓ Strafed left and right")
    print("  ✓ Rotated clockwise and counter-clockwise")


if __name__ == "__main__":
    main()
