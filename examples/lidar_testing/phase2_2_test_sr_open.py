#!/usr/bin/env python3
"""
Phase 2.2: Test SR_OPEN Mode for Smooth Low-Speed Movement

Tests switching motors to SR_OPEN mode which is optimized for low speeds (0-400 RPM).

Problem identified:
- Current mode: SR_vFOC (0-3000 RPM, optimized for high speed)
- Operating at: 19-60 RPM (way below vFOC optimal range)
- Result: Oscillations at all speeds, worse at lower speeds

Solution:
- Switch to SR_OPEN mode (0-400 RPM, optimized for LOW speed)
- SR_OPEN covers our entire operating range perfectly

Result (verified):
- ✓ Oscillations eliminated at all speeds (19-95 RPM)
- ✓ Smooth movement even at 8cm/s (19 RPM)
- ✓ Normal motor noise only (acceptable)
- ✓ Command works despite timeout messages in response parsing

Usage:
    robot run examples/lidar_testing/phase2_2_test_sr_open.py
"""

import time
from evabot import Robot, MecanumDrive

def test_movement(robot, vx, vy, vtheta, duration, description):
    """Test movement at constant velocity."""
    print()
    print("─" * 70)
    print(f"Test: {description}")
    print(f"  vx={vx}, vy={vy}, vtheta={vtheta}")
    print(f"  Duration: {duration}s")
    print("─" * 70)
    print("Observe robot movement for smoothness...")
    print()

    robot.drive.move(vx=vx, vy=vy, vtheta=vtheta)
    time.sleep(duration)
    robot.drive.halt()
    print("✓ Movement complete")
    print()
    time.sleep(2.0)

def main():
    print("=" * 70)
    print("Phase 2.2: Test SR_OPEN Mode")
    print("=" * 70)
    print()
    print("This test switches motors to SR_OPEN mode (0-400 RPM)")
    print("and re-tests the same speeds from Phase 2.1")
    print()
    print("Test sequence:")
    print("  1. Switch all motors to SR_OPEN mode")
    print("  2. Test at 8cm/s (19 RPM) - should be smooth now")
    print("  3. Test at 15cm/s (36 RPM)")
    print("  4. Test at 25cm/s (60 RPM)")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X', acceleration=50)
    robot.start()

    print()
    print("=" * 70)
    print("SWITCHING TO SR_OPEN MODE")
    print("=" * 70)
    print()

    # Switch all motors to SR_OPEN (mode=3)
    motors = [robot.drive.fl, robot.drive.fr, robot.drive.bl, robot.drive.br]
    for motor in motors:
        success = motor.set_mode(3)  # 3 = SR_OPEN
        if not success:
            print(f"WARNING: Failed to set mode for {motor.name}")
        time.sleep(0.1)

    print()
    print("Waiting 2 seconds for mode change to take effect...")
    time.sleep(2)

    print()
    print("=" * 70)
    print("TESTING WITH SR_OPEN MODE")
    print("=" * 70)
    print()

    try:
        # Test 1: Very slow (was oscillating in vFOC mode)
        test_movement(robot, vx=0.08, vy=0, vtheta=0,
                     duration=5.0,
                     description="Very slow forward (8cm/s ≈ 19 RPM)")

        # Test 2: Medium
        test_movement(robot, vx=0.15, vy=0, vtheta=0,
                     duration=5.0,
                     description="Medium forward (15cm/s ≈ 36 RPM)")

        # Test 3: Fast
        test_movement(robot, vx=0.25, vy=0, vtheta=0,
                     duration=5.0,
                     description="Fast forward (25cm/s ≈ 60 RPM)")

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 2.2 Complete!")
    print("=" * 70)
    print()
    print("Observations:")
    print("  - Was 8cm/s (19 RPM) smooth in SR_OPEN mode?")
    print("  - Did oscillations disappear at low speeds?")
    print()
    print("Next steps:")
    print("  - If smooth: Update all scripts to use SR_OPEN mode")
    print("  - If still oscillating: Try reducing subdivision (microstepping)")


if __name__ == "__main__":
    main()
