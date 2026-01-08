#!/usr/bin/env python3
"""
Debug: Wall Detection Diagnostic

Tests check_wall() for all 4 walls with detailed debugging output.

This will help us understand why check_wall(180) returns None
when the robot is in certain positions.

Usage:
    robot run examples/lidar_testing/debug_wall_detection.py
"""

import time
from evabot import Robot, RPLidarC1


def test_wall_detection(lidar, angle, wall_name):
    """
    Test wall detection with detailed output.

    Args:
        lidar: RPLidarC1 instance
        angle: Angle to check (degrees)
        wall_name: Human-readable name (e.g., "Front")
    """
    print()
    print("─" * 70)
    print(f"Testing {wall_name} Wall ({angle}°)")
    print("─" * 70)

    # Get basic distance first (always works)
    basic_distance = lidar.get_distance_at(angle)
    print(f"  get_distance_at({angle}°): {basic_distance:.3f}m ({basic_distance*100:.1f}cm)" if basic_distance else f"  get_distance_at({angle}°): None")

    # Get detailed wall check (might fail) - WITH DEBUG
    distance, angle_deg, quality = lidar.check_wall(angle, debug=True)

    if distance is not None:
        print(f"  ✓ check_wall() SUCCESS:")
        print(f"    - Distance:  {distance:.3f}m ({distance*100:.1f}cm)")
        print(f"    - Angle:     {angle_deg:+.2f}°")
        print(f"    - Quality:   {quality:.2f}")
    else:
        print(f"  ✗ check_wall() FAILED: returned (None, None, None)")
        print(f"    Possible reasons:")
        print(f"      1. Not enough points in ±30° range (need ≥10 points)")
        print(f"      2. Range discontinuity detected (corner/edge)")
        print(f"      3. Poor line fit (residual > 2cm)")
        print(f"      4. Wall not perpendicular to view direction (>30° deviation)")

        # Try to diagnose by checking nearby angles
        print(f"    Nearby angle scan:")
        for offset in [-30, -20, -10, 0, 10, 20, 30]:
            test_angle = (angle + offset) % 360
            d = lidar.get_distance_at(test_angle)
            if d:
                print(f"      {test_angle:3d}°: {d:.3f}m ({d*100:.1f}cm)")
            else:
                print(f"      {test_angle:3d}°: None")

    return distance, angle_deg, quality


def main():
    print("=" * 70)
    print("Wall Detection Debug Test")
    print("=" * 70)
    print()
    print("This test checks all 4 walls with detailed diagnostics.")
    print()
    print("Expected behavior:")
    print("  - If robot is centered: Should see all 4 walls")
    print("  - If robot is in corner: Might not see opposite walls")
    print("  - check_wall() is stricter than get_distance()")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    # Initialize robot
    robot = Robot()
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to stabilize...")
    time.sleep(3)

    print()
    print("=" * 70)
    print("WALL DETECTION TESTS")
    print("=" * 70)

    # Test all 4 walls
    results = {}
    results['front'] = test_wall_detection(robot.lidar, 0, "Front")
    results['right'] = test_wall_detection(robot.lidar, 90, "Right")
    results['back'] = test_wall_detection(robot.lidar, 180, "Back")
    results['left'] = test_wall_detection(robot.lidar, 270, "Left")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    print("Wall Detection Results:")
    print(f"  Front (0°):   {'✓ DETECTED' if results['front'][0] else '✗ FAILED'}")
    print(f"  Right (90°):  {'✓ DETECTED' if results['right'][0] else '✗ FAILED'}")
    print(f"  Back (180°):  {'✓ DETECTED' if results['back'][0] else '✗ FAILED'}")
    print(f"  Left (270°):  {'✓ DETECTED' if results['left'][0] else '✗ FAILED'}")

    print()
    successful = sum(1 for _, _, _ in results.values() if _ is not None)
    print(f"Success rate: {successful}/4 walls detected")

    if successful < 4:
        print()
        print("Diagnosis:")
        print("  If you can see a wall with get_distance() but check_wall() fails:")
        print("    → Likely: Robot is too close or at bad angle")
        print("    → Solution: Move robot away from walls or adjust position")
        print("  If you can't see a wall with get_distance():")
        print("    → Likely: Physical obstruction or out of lidar range")

    robot.stop()

    print()
    print("=" * 70)
    print("Debug Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
