#!/usr/bin/env python3
"""
Test Lookahead Position Control (No Lidar)

Tests the new lookahead-based position control with combined linear + angular movements.
No walls, no lidar - just pure position control testing at various speeds.

Goal: Verify no oscillations and smooth combined movements.

Usage:
    robot run examples/lidar_testing/test_lookahead_control.py
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


def test_forward(robot, distance, speed, description):
    """Test pure forward movement."""
    print()
    print("=" * 70)
    print(f"TEST: {description}")
    print("=" * 70)

    start_pose = robot.odom.pose
    t0 = time.time()

    log(f"Starting at x={start_pose.x:.3f}m, theta={math.degrees(start_pose.theta):.1f}°", t0)
    log(f"Target: Move forward {distance}m at {speed*100:.0f}cm/s", t0)

    robot.drive.set_target_position(dx=distance, dy=0, dtheta_deg=0, speed=speed)

    # Monitor until complete (with timeout)
    timeout = 15.0
    while time.time() - t0 < timeout:
        if not robot.drive._position_control_active:
            break
        time.sleep(0.1)

    end_pose = robot.odom.pose
    actual_distance = end_pose.x - start_pose.x
    error = actual_distance - distance

    log(f"Complete! x={end_pose.x:.3f}m, theta={math.degrees(end_pose.theta):.1f}°", t0)
    log(f"Actual distance: {actual_distance:.3f}m, error: {error*100:.1f}cm", t0)

    time.sleep(1.0)
    return abs(error) < 0.01  # 1cm tolerance


def test_rotation(robot, angle_deg, speed, description):
    """Test pure rotation."""
    print()
    print("=" * 70)
    print(f"TEST: {description}")
    print("=" * 70)

    start_pose = robot.odom.pose
    t0 = time.time()

    log(f"Starting at theta={math.degrees(start_pose.theta):.1f}°", t0)
    log(f"Target: Rotate {angle_deg:+.0f}° at speed={speed*100:.0f}cm/s", t0)

    robot.drive.set_target_position(dx=0, dy=0, dtheta_deg=angle_deg, speed=speed)

    # Monitor until complete
    timeout = 15.0
    while time.time() - t0 < timeout:
        if not robot.drive._position_control_active:
            break
        time.sleep(0.1)

    end_pose = robot.odom.pose
    actual_rotation = math.degrees(end_pose.theta - start_pose.theta)
    error = actual_rotation - angle_deg

    log(f"Complete! theta={math.degrees(end_pose.theta):.1f}°", t0)
    log(f"Actual rotation: {actual_rotation:+.1f}°, error: {error:+.1f}°", t0)

    time.sleep(1.0)
    return abs(error) < 3.0  # 3° tolerance


def test_combined(robot, distance, angle_deg, speed, description):
    """Test combined forward + rotation."""
    print()
    print("=" * 70)
    print(f"TEST: {description}")
    print("=" * 70)

    start_pose = robot.odom.pose
    t0 = time.time()

    log(f"Starting at x={start_pose.x:.3f}m, theta={math.degrees(start_pose.theta):.1f}°", t0)
    log(f"Target: Move {distance}m forward + rotate {angle_deg:+.0f}° at {speed*100:.0f}cm/s", t0)

    robot.drive.set_target_position(dx=distance, dy=0, dtheta_deg=angle_deg, speed=speed)

    # Monitor with periodic logging
    last_log = t0
    LOG_INTERVAL = 0.5

    timeout = 15.0
    while time.time() - t0 < timeout:
        if not robot.drive._position_control_active:
            break

        if time.time() - last_log >= LOG_INTERVAL:
            pose = robot.odom.pose
            traveled = pose.x - start_pose.x
            rotated = math.degrees(pose.theta - start_pose.theta)
            log(f"  Progress: {traveled*100:.1f}cm traveled, {rotated:+.1f}° rotated", t0)
            last_log = time.time()

        time.sleep(0.05)

    end_pose = robot.odom.pose
    actual_distance = end_pose.x - start_pose.x
    actual_rotation = math.degrees(end_pose.theta - start_pose.theta)

    dist_error = actual_distance - distance
    angle_error = actual_rotation - angle_deg

    log(f"Complete!", t0)
    log(f"  Distance: {actual_distance:.3f}m (error: {dist_error*100:.1f}cm)", t0)
    log(f"  Rotation: {actual_rotation:+.1f}° (error: {angle_error:+.1f}°)", t0)

    time.sleep(1.0)
    return abs(dist_error) < 0.01 and abs(angle_error) < 3.0


def test_square(robot, side_length, speed, description):
    """Test square pattern with 90° turns."""
    print()
    print("=" * 70)
    print(f"TEST: {description}")
    print("=" * 70)

    start_pose = robot.odom.pose
    t0_total = time.time()

    log(f"Starting square: {side_length}m sides at {speed*100:.0f}cm/s", t0_total)

    for i in range(4):
        log(f"Side {i+1}/4: Moving forward {side_length}m...", t0_total)
        robot.drive.set_target_position(dx=side_length, dy=0, dtheta_deg=0, speed=speed)

        # Wait for completion
        while robot.drive._position_control_active:
            time.sleep(0.05)

        log(f"Side {i+1}/4: Rotating 90°...", t0_total)
        robot.drive.set_target_position(dx=0, dy=0, dtheta_deg=90, speed=speed)

        # Wait for completion
        while robot.drive._position_control_active:
            time.sleep(0.05)

    end_pose = robot.odom.pose
    final_dist = math.sqrt((end_pose.x - start_pose.x)**2 + (end_pose.y - start_pose.y)**2)
    final_angle = math.degrees(end_pose.theta - start_pose.theta)

    elapsed = time.time() - t0_total

    log(f"Square complete! Time: {elapsed:.2f}s", t0_total)
    log(f"  Return accuracy: {final_dist*100:.1f}cm from start", t0_total)
    log(f"  Angle accuracy: {final_angle:+.1f}° from start", t0_total)

    time.sleep(1.0)
    return final_dist < 0.05 and abs(final_angle % 360) < 5.0


def main():
    print("=" * 70)
    print("Lookahead Position Control Test")
    print("=" * 70)
    print()
    print("Tests:")
    print("  1. Pure forward movement (slow, medium, fast)")
    print("  2. Pure rotation (various angles)")
    print("  3. Combined forward + rotation (simultaneous)")
    print("  4. Square pattern (accuracy test)")
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
    print("Origin reset. Starting tests...")

    results = []

    try:
        # Test 1: Pure forward at different speeds
        results.append(("Forward 0.5m slow", test_forward(robot, 0.5, 0.1, "Forward 0.5m at 10cm/s (slow)")))
        results.append(("Forward 0.5m medium", test_forward(robot, 0.5, 0.3, "Forward 0.5m at 30cm/s (medium)")))
        results.append(("Forward 0.5m fast", test_forward(robot, 0.5, 0.5, "Forward 0.5m at 50cm/s (fast)")))

        # Test 2: Pure rotation
        results.append(("Rotate 90°", test_rotation(robot, 90, 0.2, "Rotate 90° CCW")))
        results.append(("Rotate -90°", test_rotation(robot, -90, 0.2, "Rotate 90° CW")))
        results.append(("Rotate 180°", test_rotation(robot, 180, 0.2, "Rotate 180°")))

        # Test 3: Combined movements (this is the key test!)
        results.append(("Forward + rotate (slow)", test_combined(robot, 0.5, 45, 0.1, "0.5m forward + 45° rotation at 10cm/s")))
        results.append(("Forward + rotate (medium)", test_combined(robot, 0.5, 45, 0.3, "0.5m forward + 45° rotation at 30cm/s")))
        results.append(("Forward + rotate (fast)", test_combined(robot, 0.5, 45, 0.5, "0.5m forward + 45° rotation at 50cm/s")))

        # Test 4: Square pattern
        robot.drive.zero_position()
        results.append(("Square 0.5m", test_square(robot, 0.5, 0.3, "Square pattern 0.5m sides")))

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Stop robot
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    # Print results
    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")

    print()
    print(f"Passed: {passed}/{total} tests")

    if passed == total:
        print()
        print("🎉 All tests passed! Lookahead control working correctly.")
    else:
        print()
        print("⚠️  Some tests failed. Check for oscillations or tuning issues.")

    print()
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
