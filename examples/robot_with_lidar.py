#!/usr/bin/env python3
"""
Example: Robot with Lidar
Demonstrates using RPLidar C1 with a Robot instance.
"""

import time
from evabot import Robot
from evabot.components.sensors import RPLidarC1


def test_robot_with_lidar():
    """Test lidar attached to robot."""
    print("=" * 60)
    print("Robot with Lidar Test")
    print("=" * 60)
    print()

    # Create robot
    robot = Robot()

    # Attach lidar
    print("Attaching lidar to robot...")
    robot.lidar = RPLidarC1()
    print()

    # Start robot (starts all attached components)
    print("Starting robot...")
    robot.start()
    print()

    # Wait for scan data
    print("Waiting for lidar data (2 seconds)...")
    time.sleep(2)
    print()

    # Access lidar through robot
    print("=" * 60)
    print("Lidar Readings (via robot.lidar):")
    print("=" * 60)
    print(f"  Front: {robot.lidar.front:.2f}m" if robot.lidar.front else "  Front: No reading")
    print(f"  Left:  {robot.lidar.left:.2f}m" if robot.lidar.left else "  Left:  No reading")
    print(f"  Right: {robot.lidar.right:.2f}m" if robot.lidar.right else "  Right: No reading")
    print()

    # Simple obstacle detection
    print("=" * 60)
    print("Obstacle Detection:")
    print("=" * 60)

    SAFE_DISTANCE = 0.5  # meters

    front = robot.lidar.front
    if front:
        if front < SAFE_DISTANCE:
            print(f"  ⚠️  OBSTACLE AHEAD at {front:.2f}m!")
        else:
            print(f"  ✅ Front clear ({front:.2f}m)")

    left = robot.lidar.left
    if left:
        if left < SAFE_DISTANCE:
            print(f"  ⚠️  OBSTACLE LEFT at {left:.2f}m!")
        else:
            print(f"  ✅ Left clear ({left:.2f}m)")

    right = robot.lidar.right
    if right:
        if right < SAFE_DISTANCE:
            print(f"  ⚠️  OBSTACLE RIGHT at {right:.2f}m!")
        else:
            print(f"  ✅ Right clear ({right:.2f}m)")

    print()

    # Continuous monitoring
    print("=" * 60)
    print("Continuous Monitoring (3 seconds)")
    print("=" * 60)

    try:
        for i in range(30):
            front = robot.lidar.front
            left = robot.lidar.left
            right = robot.lidar.right

            status = f"[{i/10:.1f}s]"
            if front:
                status += f" F:{front:.2f}m"
            if left:
                status += f" L:{left:.2f}m"
            if right:
                status += f" R:{right:.2f}m"

            print(status)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped by user")

    print()

    # Stop robot
    print("Stopping robot...")
    robot.stop()
    print()

    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_robot_with_lidar()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
