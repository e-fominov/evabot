#!/usr/bin/env python3
"""
Phase 2.1: Smooth Movement Investigation

Investigates and fixes movement jitter observed in Phase 2.

Problem (identified):
- Robot movement has noticeable oscillating jitter during constant velocity
- Jitter is NOT related to lidar feedback (happens without lidar control)
- Jitter only occurs under load (smooth when wheels in air)
- Same in all directions, doesn't increase with speed

Root Cause (identified):
- Motors in SR_vFOC mode (0-3000 RPM, optimized for HIGH speed)
- Operating at 19-60 RPM (way below vFOC optimal range)
- Result: Low-speed resonance causing oscillations under load

Solution (confirmed working):
- Switch motors to SR_OPEN mode (0-400 RPM, optimized for LOW speed)
- SR_OPEN covers entire operating range (19-60 RPM) perfectly
- Use acceleration=50 for smooth ramping
- Result: Smooth movement at all speeds, normal motor noise only

Implementation:
- Call motor.set_mode(3) for each motor (3 = SR_OPEN)
- Command: 0x82, mode=3
- Note: Response parsing may timeout but command works (check behavior)

Usage:
    robot run examples/lidar_testing/phase2_1_smooth_movement.py
"""

import time
from evabot import Robot, MecanumDrive

def test_movement(robot, vx, vy, vtheta, duration, description):
    """
    Test movement at constant velocity.

    Args:
        robot: Robot instance
        vx, vy, vtheta: Velocities
        duration: Test duration in seconds
        description: Test description
    """
    print()
    print("─" * 70)
    print(f"Test: {description}")
    print(f"  vx={vx}, vy={vy}, vtheta={vtheta}")
    print(f"  Duration: {duration}s")
    print("─" * 70)
    print("Observe robot movement for smoothness...")
    print()

    # Start movement
    robot.drive.move(vx=vx, vy=vy, vtheta=vtheta)

    # Hold for duration (no updates - constant velocity command)
    time.sleep(duration)

    # Stop
    robot.drive.halt()
    print("✓ Movement complete")
    print()
    time.sleep(2.0)  # Pause between tests

def main():
    print("=" * 70)
    print("Phase 2.1: Smooth Movement Investigation")
    print("=" * 70)
    print()
    print("This test moves robot at constant velocities")
    print("Observe if movement is smooth or has jitter")
    print()
    print("Test sequence:")
    print("  1. Very slow (8cm/s) - Current speed, likely oscillates")
    print("  2. Medium (15cm/s)")
    print("  3. Fast (25cm/s) - Target speed, should be smooth")
    print("  4. Very fast (40cm/s)")
    print()
    print("Observe at which speed oscillations disappear")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Initialize robot (no lidar needed)
    # Using acceleration=50 for smoother motion (default was 2, too jerky)
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X', acceleration=50)
    robot.start()

    print()
    print("=" * 70)
    print("TESTING SPEED RANGE TO FIND OSCILLATION THRESHOLD")
    print("=" * 70)
    print()
    print("Speed calculations (wheel_radius=0.04m):")
    print("  0.08 m/s ≈ 19 RPM")
    print("  0.15 m/s ≈ 36 RPM")
    print("  0.25 m/s ≈ 60 RPM")
    print("  0.40 m/s ≈ 95 RPM")
    print()

    try:
        # Test 1: Very slow (current speed)
        test_movement(robot, vx=0.08, vy=0, vtheta=0,
                     duration=5.0,
                     description="Very slow forward (8cm/s ≈ 19 RPM)")

        # Test 2: Medium
        test_movement(robot, vx=0.15, vy=0, vtheta=0,
                     duration=5.0,
                     description="Medium forward (15cm/s ≈ 36 RPM)")

        # Test 3: Fast (target)
        test_movement(robot, vx=0.25, vy=0, vtheta=0,
                     duration=5.0,
                     description="Fast forward (25cm/s ≈ 60 RPM)")

        # Test 4: Very fast
        test_movement(robot, vx=0.40, vy=0, vtheta=0,
                     duration=5.0,
                     description="Very fast forward (40cm/s ≈ 95 RPM)")

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 2.1 Complete!")
    print("=" * 70)
    print()
    print("Observations:")
    print("  - At which speed did oscillations disappear?")
    print("  - Was 25cm/s (60 RPM) smooth as expected?")
    print()
    print("Next steps:")
    print("  - If smooth at 25cm/s: Use this as minimum speed")
    print("  - If still oscillating: Try SR_OPEN mode (optimized for low speed)")
    print("  - If still oscillating: Reduce microstepping/subdivision via 0x84 command")


if __name__ == "__main__":
    main()
