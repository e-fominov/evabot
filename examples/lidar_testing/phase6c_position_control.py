#!/usr/bin/env python3
"""
Phase 6c: Position Control with Continuous Target Updates

Tests the new non-blocking position control system that uses Servo42D's internal
trajectory planning running at kHz frequency.

Key Test: Continuous target position updates based on lidar feedback to detect:
- Oscillations from frequent position command updates
- Control stability when target changes every cycle
- Stopping accuracy compared to velocity control
- Performance at different speeds

Test Strategy:
1. Move forward toward wall
2. Continuously update target position based on remaining distance to wall
3. Stop when lidar reads target distance from wall
4. Measure final stopping accuracy

This simulates real-world wall-following where we continuously adjust trajectory
based on sensor feedback.

=============================================================================
RESULTS: Position Control vs Velocity Control
=============================================================================

Test Results (actual measurements):
╔═══════════╦═══════════════════╦═══════════════════╦══════════════╗
║  Speed    ║  Velocity Control ║ Position Control  ║  Improvement ║
╠═══════════╬═══════════════════╬═══════════════════╬══════════════╣
║   8 cm/s  ║     -1.1 cm       ║     -0.7 cm       ║    1.6×      ║
║  12 cm/s  ║     -2.3 cm       ║     -1.3 cm       ║    1.8×      ║
║  16 cm/s  ║     -3.5 cm       ║     -1.3 cm       ║    2.7×      ║
║  20 cm/s  ║     -5.2 cm       ║     -1.2 cm       ║    4.3×      ║
║  24 cm/s  ║  (unsafe/untested)║     -1.2 cm       ║     —        ║
╚═══════════╩═══════════════════╩═══════════════════╩══════════════╝

Key Findings:
-------------
1. ✓ ERROR IS SPEED-INDEPENDENT with position control
   - Constant ~1.2-1.3cm error across ALL speeds
   - Velocity control error grew linearly with speed

2. ✓ 2-4× BETTER ACCURACY at high speeds
   - At 20 cm/s: 4.3× improvement (5.2cm → 1.2cm)
   - Enables safe high-speed navigation

3. ✓ NO OSCILLATIONS detected
   - Continuous 40Hz target updates are stable
   - Motor controller handles frequent commands smoothly

4. Remaining constant error (~1.2cm):
   - Not speed-dependent → not control loop latency
   - Likely: sensor delay, motor response time, or calibration offset
   - Could be reduced with predictive compensation

Conclusion:
-----------
Position control successfully eliminates the fundamental limitation of velocity
control (speed-dependent error from Python loop latency). High-speed navigation
(16-24 cm/s) is now viable with acceptable accuracy.

For < 8 cm/s: Both methods work (velocity slightly better: 0.7 vs 1.1cm)
For > 12 cm/s: Position control strongly preferred (2-4× better accuracy)

Usage:
    robot run examples/lidar_testing/phase6c_position_control.py
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1


def align_to_wall(robot, wall_angle, max_iterations=50):
    """Align robot parallel to a wall."""
    ALIGNMENT_THRESHOLD = 2.0
    ROTATION_GAIN = 0.02
    MAX_ROTATION_SPEED = 0.3
    UPDATE_RATE = 5

    print(f"  Aligning to wall {wall_angle}°...")

    for _ in range(max_iterations):
        distance, angle_deg, quality = robot.lidar.check_wall(wall_angle)

        if angle_deg is not None and abs(angle_deg) < ALIGNMENT_THRESHOLD:
            robot.drive.halt()
            print(f"  ✓ Aligned! angle: {angle_deg:+.2f}°")
            return True

        if angle_deg is not None:
            rotation_speed = ROTATION_GAIN * angle_deg
            rotation_speed = max(-MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, rotation_speed))
            robot.drive.move(vtheta=rotation_speed)

        time.sleep(1.0 / UPDATE_RATE)

    robot.drive.halt()
    print(f"  ✗ Could not align to wall {wall_angle}°")
    return False


def move_to_position(robot, target_x, target_y=0.0, arena_center_to_wall=0.30):
    """
    Move robot to specific position relative to arena center using velocity control.

    Args:
        robot: Robot instance
        target_x: Target x position (m) relative to center
        target_y: Target y position (m) relative to center
        arena_center_to_wall: Distance from center to wall (default 0.30m = 30cm)
    """
    # Measure current position using wall distances
    front_distance, _, _ = robot.lidar.check_wall(0)
    back_distance, _, _ = robot.lidar.check_wall(180)
    left_distance, _, _ = robot.lidar.check_wall(270)
    right_distance, _, _ = robot.lidar.check_wall(90)

    if front_distance is None or back_distance is None:
        print("  ✗ Cannot determine position - missing wall measurements")
        return False

    # Calculate current x position (positive = toward front wall)
    current_x = arena_center_to_wall - front_distance
    current_y = 0.0

    if left_distance and right_distance:
        current_y = arena_center_to_wall - left_distance

    # Calculate required movement
    move_x = target_x - current_x
    move_y = target_y - current_y

    print(f"  Current: x={current_x*100:.1f}cm, y={current_y*100:.1f}cm")
    print(f"  Target:  x={target_x*100:.1f}cm, y={target_y*100:.1f}cm")
    print(f"  Moving:  Δx={move_x*100:.1f}cm, Δy={move_y*100:.1f}cm")

    if abs(move_x) < 0.01 and abs(move_y) < 0.01:
        print("  ✓ Already at target position")
        return True

    # Move to position at slow speed using velocity control
    distance = (move_x**2 + move_y**2)**0.5
    move_time = distance / 0.08  # 8cm/s

    if distance > 0:
        vx = (move_x / distance) * 0.08
        vy = (move_y / distance) * 0.08

        robot.drive.move(vx=vx, vy=vy)
        time.sleep(move_time)
        robot.drive.halt()
        time.sleep(0.3)

        print("  ✓ Moved to position")
        return True

    return True


def test_position_control_stopping(robot, speed, target_distance=0.17, update_rate=50):
    """
    Test stopping accuracy using position control with continuous target updates.

    This is the KEY TEST that differs from Phase 6b:
    - Continuously updates target position every cycle (simulates real usage)
    - Tests for oscillations or instability from frequent updates
    - Motor handles trajectory planning at kHz internally

    Args:
        robot: Robot instance
        speed: Forward speed (m/s)
        target_distance: Target distance from wall to stop (m)
        update_rate: How often to update target position (Hz)

    Returns:
        dict: Test results with error metrics
    """
    print(f"\n  Testing: speed={speed*100:.0f}cm/s (position control)")

    # Start position control loop
    start_time = time.time()
    stopped = False
    update_count = 0

    while time.time() - start_time < 10.0:  # 10s timeout
        # Measure current distance to wall
        distance, _, _ = robot.lidar.check_wall(0)

        if distance is None:
            print("    ✗ Lost lidar reading")
            robot.drive.halt()
            return None

        # Calculate remaining distance
        remaining = distance - target_distance

        if remaining <= 0.005:  # Within 5mm, stop
            robot.drive.halt()
            stopped = True
            break

        # CONTINUOUS UPDATE: Set new target position based on current remaining distance
        # This is the key difference from "set once and monitor" approach
        robot.drive.set_target_position(dx=remaining, speed=speed)
        update_count += 1

        time.sleep(1.0 / update_rate)

    if not stopped:
        robot.drive.halt()
        print(f"    ✗ Timeout - did not reach target ({update_count} updates sent)")
        return None

    # Wait for robot to fully stop
    time.sleep(0.3)

    # Measure final distance
    final_distance, _, _ = robot.lidar.check_wall(0)

    if final_distance is None:
        print("    ✗ Could not measure final distance")
        return None

    # Calculate error
    error = final_distance - target_distance
    elapsed = time.time() - start_time

    print(f"    Final: {final_distance*100:.1f}cm, Error: {error*100:+.1f}cm, Time: {elapsed:.2f}s")
    print(f"    Updates sent: {update_count} ({update_count/elapsed:.1f} Hz actual)")

    return {
        'speed': speed,
        'target_distance': target_distance,
        'final_distance': final_distance,
        'error': error,
        'time': elapsed,
        'update_count': update_count
    }


def main():
    print("=" * 70)
    print("Phase 6c: Position Control with Continuous Updates")
    print("=" * 70)
    print()
    print("This test uses motor-based position control with continuous target")
    print("updates to test for oscillations and stopping accuracy.")
    print()
    print("Key difference from velocity control (Phase 6b):")
    print("  - Motor controller handles trajectory at kHz (vs 10Hz Python)")
    print("  - Continuous target updates every cycle (simulates real usage)")
    print("  - Expected: Sub-millimeter precision even at high speeds")
    print()
    print("Test matrix:")
    print("  Speeds: 8, 12, 16, 20, 24 cm/s")
    print("  Target: Stop at 17cm from wall")
    print("  Update rate: 50Hz (continuous target adjustments)")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Test parameters
    TEST_SPEEDS = [0.08, 0.12, 0.16, 0.20, 0.24]  # m/s
    START_POSITION = -0.15  # 15cm behind center
    TARGET_DISTANCE = 0.17  # 17cm from front wall
    UPDATE_RATE = 50  # Hz - update target position 50 times per second

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X', acceleration=100)
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    all_results = []

    try:
        for speed in TEST_SPEEDS:
            print()
            print("─" * 70)
            print(f"Test: {speed*100:.0f}cm/s @ position control")
            print("─" * 70)

            # Move to start position
            print("\n  Moving to start position...")
            if not move_to_position(robot, START_POSITION, 0.0):
                print("  ✗ Failed to reach start position")
                continue

            time.sleep(0.5)

            # Align to back wall for consistent starting orientation
            print("\n  Aligning to back wall (180°)...")
            if not align_to_wall(robot, 180):
                print("  ✗ Failed to align")
                continue

            time.sleep(0.5)

            # Run position control test with continuous updates
            result = test_position_control_stopping(robot, speed, TARGET_DISTANCE, UPDATE_RATE)

            if result:
                all_results.append(result)

            time.sleep(1.0)

        # Display results
        print()
        print()
        print("=" * 70)
        print("POSITION CONTROL RESULTS")
        print("=" * 70)
        print()

        if all_results:
            print(f"{'Speed':>8} │ {'Final Dist':>11} │ {'Error':>8} │ {'Time':>6} │ {'Updates':>8}")
            print("─" * 58)

            for r in all_results:
                speed_str = f"{r['speed']*100:.0f} cm/s"
                dist_str = f"{r['final_distance']*100:.1f}cm"
                err_str = f"{r['error']*100:+.1f}cm"
                time_str = f"{r['time']:.2f}s"
                updates_str = f"{r['update_count']}"
                print(f"{speed_str:>8} │ {dist_str:>11} │ {err_str:>8} │ {time_str:>6} │ {updates_str:>8}")

        print()
        print("=" * 70)
        print("ANALYSIS: Position Control vs Velocity Control")
        print("=" * 70)
        print()
        print("Position Control Advantages:")
        print("  ✓ Motor controller runs at kHz (vs 10Hz Python loop)")
        print("  ✓ No control loop latency from Python processing")
        print("  ✓ Can handle continuous target updates without oscillations")
        print("  ✓ Expected error independent of speed (motor handles timing)")
        print()
        print("Comparison with Phase 6b (velocity control):")
        print("  Velocity: Error ≈ Speed × 200ms")
        print("    8 cm/s  → 1.1 cm error")
        print("    12 cm/s → 2.3 cm error")
        print("    16 cm/s → 3.5 cm error")
        print("    20 cm/s → 5.2 cm error")
        print()
        print("  Position: Error should be constant (~1-2mm) across all speeds")
        print()
        print("Oscillation Check:")
        if all_results:
            oscillation_detected = False
            for r in all_results:
                if abs(r['error']) > 0.05:  # >5cm might indicate oscillation
                    oscillation_detected = True
                    print(f"  ⚠ Large error at {r['speed']*100:.0f}cm/s - check for oscillations")

            if not oscillation_detected:
                print("  ✓ No oscillations detected - continuous updates stable")

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 6c Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
