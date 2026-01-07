#!/usr/bin/env python3
"""
Simple test of get_clearance() and check_wall() functions.
Tests with real lidar data without needing full robot setup.
"""

from evabot import Robot, RPLidarC1
import time
import math


def print_scan_summary(lidar):
    """Print basic scan info for all 4 directions."""
    print("\n" + "=" * 60)
    print("LIDAR SCAN SUMMARY")
    print("=" * 60)

    directions = [
        ("Front (0°)", 0),
        ("Right (90°)", 90),
        ("Back (180°)", 180),
        ("Left (270°)", 270),
    ]

    for name, angle in directions:
        dist = lidar.get_distance_at(angle)
        if dist:
            print(f"  {name:15s}: {dist:.3f}m ({dist*100:.1f}cm)")
        else:
            print(f"  {name:15s}: No data")


def test_get_clearance(lidar):
    """Test get_clearance() function in all directions."""
    print("\n" + "=" * 60)
    print("TEST: get_clearance() - Rectangular Clearance Check")
    print("=" * 60)
    print("This checks how far the robot can safely travel,")
    print("accounting for the full 20cm robot width.\n")

    directions = [
        ("Forward (0°)", 0),
        ("Right (90°)", 90),
        ("Backward (180°)", 180),
        ("Left (270°)", 270),
    ]

    for name, angle in directions:
        clearance = lidar.get_clearance(angle, robot_width=0.20)
        if clearance:
            print(f"  {name:18s}: {clearance:.3f}m ({clearance*100:.1f}cm)")
            if clearance < 0.15:
                print(f"                      ⚠ Too close! (< 15cm)")
            elif clearance > 0.25:
                print(f"                      ✓ Opening detected! (> 25cm)")
        else:
            print(f"  {name:18s}: No data")


def test_check_wall(lidar):
    """Test check_wall() function in all directions."""
    print("\n" + "=" * 60)
    print("TEST: check_wall() - Wall Detection and Alignment")
    print("=" * 60)
    print("This checks if there's a continuous wall and measures alignment.\n")

    directions = [
        ("Front (0°)", 0),
        ("Right (90°)", 90),
        ("Back (180°)", 180),
        ("Left (270°)", 270),
    ]

    for name, angle in directions:
        wall_info = lidar.check_wall(angle)

        if wall_info:
            distance, angle_error = wall_info
            print(f"  {name:18s}: Wall detected!")
            print(f"                      Distance: {distance:.3f}m ({distance*100:.1f}cm)")
            print(f"                      Angle error: {angle_error:+.4f}m ({angle_error*100:+.2f}cm)")

            if abs(angle_error) < 0.01:
                print(f"                      ✓ Well aligned (< 1cm error)")
            else:
                direction = "toward wall" if angle_error > 0 else "away from wall"
                print(f"                      → Need to turn {direction}")
        else:
            print(f"  {name:18s}: No continuous wall (corner/opening/no data)")


def continuous_monitoring(lidar):
    """Continuously monitor clearance and wall info."""
    print("\n" + "=" * 60)
    print("CONTINUOUS MONITORING")
    print("=" * 60)
    print("Monitoring front clearance and right wall (if any).")
    print("Press Ctrl-C to stop.\n")

    try:
        while True:
            # Front clearance
            front_clear = lidar.get_clearance(0)

            # Right wall
            right_wall = lidar.check_wall(90)

            # Print status line
            status = f"Front: "
            if front_clear:
                status += f"{front_clear:.3f}m ({front_clear*100:.1f}cm)"
            else:
                status += "No data"

            status += " | Right wall: "
            if right_wall:
                distance, angle_error = right_wall
                status += f"{distance:.3f}m, error {angle_error:+.3f}m"
            else:
                status += "Not detected"

            print(status, end='\r')
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def main():
    print("=" * 60)
    print("Lidar Functions Test")
    print("=" * 60)
    print("Testing get_clearance() and check_wall() functions")
    print("with real lidar data.\n")

    print("Starting lidar...")

    # Create robot with just lidar
    robot = Robot()
    robot.lidar = RPLidarC1()
    robot.start()

    print("Waiting for lidar to initialize...")
    time.sleep(3)  # Give lidar time to start scanning

    try:
        # Test 1: Show raw scan summary
        print_scan_summary(robot.lidar)

        # Test 2: Test get_clearance
        test_get_clearance(robot.lidar)

        # Test 3: Test check_wall
        test_check_wall(robot.lidar)

        # Test 4: Continuous monitoring
        print("\n\nPress Enter to start continuous monitoring (Ctrl-C to stop)...")
        input()
        continuous_monitoring(robot.lidar)

        print("\n" + "=" * 60)
        print("All tests complete!")
        print("=" * 60)

    finally:
        print("\nStopping lidar...")
        robot.stop()


if __name__ == "__main__":
    main()
