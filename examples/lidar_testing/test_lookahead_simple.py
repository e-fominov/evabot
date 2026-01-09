#!/usr/bin/env python3
"""
Simple Lookahead Control Test

Just two tests to verify basic functionality:
1. Move forward 20cm (pure linear)
2. Move forward 20cm with constant 30 deg/sec rotation

Usage:
    robot run examples/lidar_testing/test_lookahead_simple.py
"""

import time
import math
from evabot import Robot, MecanumDrive


def log(msg, t0=None):
    """Print message with timestamp."""
    if t0 is not None:
        elapsed = (time.time() - t0) * 1000  # milliseconds
        print(f"[+{elapsed:6.1f}ms] {msg}")
    else:
        print(f"[{time.time():.3f}] {msg}")


def main():
    print("=" * 70)
    print("Simple Lookahead Control Test")
    print("=" * 70)
    print()
    print("Test 1: Move forward 20cm")
    print("Test 2: Move forward 20cm with 30 deg/sec rotation")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern="X", acceleration=100)
    robot.start()

    print()
    print("Waiting for initialization...")
    time.sleep(2)

    # Reset origin
    robot.drive.zero_position()
    print()
    print("Origin reset.")
    print()

    try:
        # Test 1: Pure forward 20cm
        print("=" * 70)
        print("TEST 1: Forward 20cm (pure linear)")
        print("=" * 70)

        start_pose = robot.odom.pose
        t0 = time.time()

        log(f"Start: x={start_pose.x*100:.1f}cm, theta={math.degrees(start_pose.theta):.1f}°", t0)

        # Use position control for 20cm forward
        robot.drive.set_target_position(dx=0.20, dy=0, dtheta_deg=0, speed=0.2)

        # Monitor with logging every 200ms
        last_log = t0
        LOG_INTERVAL = 0.2

        while time.time() - t0 < 5.0:  # 5s timeout
            if not robot.drive._position_control_active:
                break

            if time.time() - last_log >= LOG_INTERVAL:
                pose = robot.odom.pose
                traveled = (pose.x - start_pose.x) * 100
                rotated = math.degrees(pose.theta - start_pose.theta)
                log(f"  x={traveled:+6.1f}cm, theta={rotated:+6.1f}°", t0)
                last_log = time.time()

            time.sleep(0.05)

        end_pose = robot.odom.pose
        actual_dist = (end_pose.x - start_pose.x) * 100
        actual_angle = math.degrees(end_pose.theta - start_pose.theta)

        log(f"END: x={actual_dist:+6.1f}cm, theta={actual_angle:+6.1f}°", t0)
        log(f"Error: {actual_dist - 20.0:+.1f}cm, angle drift: {actual_angle:+.1f}°", t0)

        time.sleep(2)

        # Test 2: Forward 20cm with constant rotation
        print()
        print("=" * 70)
        print("TEST 2: Forward 20cm + 30 deg/sec rotation")
        print("=" * 70)

        # Calculate required rotation for the movement
        # If moving at 0.2 m/s for 0.2m, time = 1 second
        # At 30 deg/sec for 1 second = 30 degrees total
        estimated_time = 0.20 / 0.2  # distance / speed
        target_rotation = 30 * estimated_time  # deg/sec * time

        start_pose = robot.odom.pose
        t0 = time.time()

        log(f"Start: x={start_pose.x*100:.1f}cm, theta={math.degrees(start_pose.theta):.1f}°", t0)
        log(f"Target: 20cm forward + ~{target_rotation:.0f}° rotation", t0)

        # Use position control for combined movement
        robot.drive.set_target_position(dx=0.20, dy=0, dtheta_deg=target_rotation, speed=0.2)

        # Monitor
        last_log = t0

        while time.time() - t0 < 5.0:  # 5s timeout
            if not robot.drive._position_control_active:
                break

            if time.time() - last_log >= LOG_INTERVAL:
                pose = robot.odom.pose
                traveled = (pose.x - start_pose.x) * 100
                rotated = math.degrees(pose.theta - start_pose.theta)
                log(f"  x={traveled:+6.1f}cm, theta={rotated:+6.1f}°", t0)
                last_log = time.time()

            time.sleep(0.05)

        end_pose = robot.odom.pose
        actual_dist = (end_pose.x - start_pose.x) * 100
        actual_angle = math.degrees(end_pose.theta - start_pose.theta)

        log(f"END: x={actual_dist:+6.1f}cm, theta={actual_angle:+6.1f}°", t0)
        log(f"Error: distance={actual_dist - 20.0:+.1f}cm, rotation={actual_angle - target_rotation:+.1f}°", t0)

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Stop robot
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
