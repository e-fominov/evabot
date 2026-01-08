#!/usr/bin/env python3
"""
Phase 6b: Stopping Accuracy Test

Isolates the stopping accuracy problem by testing different speed/acceleration
combinations in a controlled environment.

Test Setup:
- Arena: 60×60cm, center at (0,0)
- Front wall at x=+30cm
- Start position: x=-15cm (15cm behind center)
- Move forward 28cm → target: 17cm from front wall
- Align to back wall before each test for consistent starting position
- Measure stopping error for each speed/acceleration combo

Test Matrix:
- Speeds: 8, 12, 16, 20, 24 cm/s
- Accelerations: 25, 50, 100, 150, 200
- Total: 25 combinations

Goal: Find optimal acceleration for each speed to minimize stopping error.
Target: Stop at 17cm from front wall (safe margin to avoid collisions)

=============================================================================
KEY FINDINGS: Fundamental Limitation of Velocity Control + Lidar Feedback
=============================================================================

Test Results (UPDATE_RATE = 10 Hz):
╔═══════════╦══════════════╦═══════════════════════════════════════════════╗
║  Speed    ║  Avg Error   ║  Error Pattern                                ║
╠═══════════╬══════════════╬═══════════════════════════════════════════════╣
║   8 cm/s  ║   -1.1 cm    ║  Consistent across all accelerations          ║
║  12 cm/s  ║   -2.3 cm    ║  Slight improvement with accel=200 (-1.7cm)   ║
║  16 cm/s  ║   -3.5 cm    ║  Accel helps: -2.8cm (200) vs -4.5cm (100)    ║
║  20 cm/s  ║   -5.2 cm    ║  Large overshoot regardless of acceleration   ║
╚═══════════╩══════════════╩═══════════════════════════════════════════════╝

Root Cause Analysis:
---------------------
The velocity-control approach has a FUNDAMENTAL LIMITATION due to control loop
frequency. The robot overshoots the target because of the delay between:
  1. Lidar detects: distance ≤ target
  2. Python processes measurement
  3. halt() command sent to motors
  4. Motors physically decelerate to stop

Mathematical Model:
-------------------
  Error ≈ Speed × (2 × Update_Period)

  At 10Hz (100ms period):
    - 8 cm/s  → ~1.6 cm theoretical, observed ~1.1 cm
    - 12 cm/s → ~2.4 cm theoretical, observed ~2.3 cm ✓
    - 16 cm/s → ~3.2 cm theoretical, observed ~3.5 cm ✓
    - 20 cm/s → ~4.0 cm theoretical, observed ~5.2 cm

  The 2× multiplier accounts for:
    - Lidar scan completion time
    - Python processing delay
    - CAN bus communication latency
    - Motor deceleration distance (physical momentum)

Why Acceleration Has Limited Effect:
------------------------------------
Higher motor acceleration (e.g., 200 vs 25) helps slightly by reducing
deceleration distance, but cannot overcome the control loop latency.
The robot is already traveling at full speed when it detects the wall,
so the majority of error comes from the delay, not the deceleration.

Alternative Solutions:
----------------------
1. INCREASE CONTROL FREQUENCY
   - 50 Hz would reduce per-cycle travel to 1/5
   - Error at 20 cm/s: ~4 cm → ~0.8 cm (theoretical)
   - Limited by Python + lidar scan rate

2. PREDICTIVE COMPENSATION
   - Calculate overshoot based on speed
   - Stop early: stop_when = target + (speed × compensation_factor)
   - Requires calibration for each speed

3. POSITION CONTROL MODE (Most Robust)
   - Use Servo42D internal trajectory planning
   - Command: "move forward 30cm", motor handles acceleration/deceleration
   - Motor controller runs at kHz frequency → sub-millimeter precision
   - Eliminates Python control loop bottleneck
   - Recommended for high-speed navigation

Conclusion:
-----------
For speeds > 12 cm/s, velocity control with 10Hz lidar feedback produces
unacceptable position errors (>2cm). Either:
  - Limit speed to ≤12 cm/s with current approach
  - Implement position control using motor's internal trajectory planner

Usage:
    robot run examples/lidar_testing/phase6b_stopping_accuracy.py
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
    Move robot to specific position relative to arena center.

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
    # front_distance = (arena_center_to_wall - current_x)
    current_x = arena_center_to_wall - front_distance
    current_y = 0.0  # Assume on centerline for simplicity

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

    # Move to position at slow speed
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


def test_stopping(robot, speed, acceleration, target_distance=0.17, update_rate=10):
    """
    Test stopping accuracy at given speed/acceleration.

    Args:
        robot: Robot instance
        speed: Forward speed (m/s)
        acceleration: Motor acceleration (0-255)
        target_distance: Target distance from wall to stop (m)
        update_rate: Control loop frequency (Hz)

    Returns:
        dict: Test results with error metrics
    """
    print(f"\n  Testing: speed={speed*100:.0f}cm/s, accel={acceleration}")

    # Update acceleration for this test
    robot.drive.fl.acceleration = acceleration
    robot.drive.fr.acceleration = acceleration
    robot.drive.bl.acceleration = acceleration
    robot.drive.br.acceleration = acceleration

    # Start moving forward
    robot.drive.move(vx=speed)

    # Monitor wall distance and stop when reaching target
    start_time = time.time()
    stopped = False

    while time.time() - start_time < 10.0:  # 10s timeout
        distance, _, _ = robot.lidar.check_wall(0)

        if distance is not None and distance <= target_distance:
            robot.drive.halt()
            stopped = True
            break

        time.sleep(1.0 / update_rate)

    if not stopped:
        robot.drive.halt()
        print("    ✗ Timeout - did not reach target")
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

    return {
        'speed': speed,
        'acceleration': acceleration,
        'target_distance': target_distance,
        'final_distance': final_distance,
        'error': error,
        'time': elapsed
    }


def main():
    print("=" * 70)
    print("Phase 6b: Stopping Accuracy Test")
    print("=" * 70)
    print()
    print("This test isolates stopping accuracy by testing different")
    print("speed/acceleration combinations")
    print()
    print("Test matrix:")
    print("  Speeds: 8, 12, 16, 20, 24 cm/s")
    print("  Accelerations: 25, 50, 100, 150, 200")
    print("  Total: 25 combinations")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Test parameters
    TEST_SPEEDS = [0.08, 0.12, 0.16, 0.20, 0.24]  # m/s
    TEST_ACCELERATIONS = [25, 50, 100, 150, 200]
    START_POSITION = -0.15  # 15cm behind center
    TARGET_DISTANCE = 0.17  # 17cm from front wall (safer margin)
    UPDATE_RATE = 10  # Hz

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X', acceleration=50)
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    all_results = []

    try:
        for speed in TEST_SPEEDS:
            for accel in TEST_ACCELERATIONS:
                print()
                print("─" * 70)
                print(f"Test: {speed*100:.0f}cm/s @ accel={accel}")
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

                # Run stopping test
                result = test_stopping(robot, speed, accel, TARGET_DISTANCE, UPDATE_RATE)

                if result:
                    all_results.append(result)

                time.sleep(1.0)

        # Display results
        print()
        print()
        print("=" * 70)
        print("STOPPING ACCURACY RESULTS")
        print("=" * 70)
        print()

        # Group by speed
        for speed in TEST_SPEEDS:
            speed_results = [r for r in all_results if r['speed'] == speed]
            if not speed_results:
                continue

            print(f"\nSpeed: {speed*100:.0f} cm/s")
            print(f"{'Accel':>6} │ {'Final Dist':>11} │ {'Error':>8} │ {'Time':>6}")
            print("─" * 40)

            for r in speed_results:
                accel_str = f"{r['acceleration']}"
                dist_str = f"{r['final_distance']*100:.1f}cm"
                err_str = f"{r['error']*100:+.1f}cm"
                time_str = f"{r['time']:.2f}s"
                print(f"{accel_str:>6} │ {dist_str:>11} │ {err_str:>8} │ {time_str:>6}")

            # Find best acceleration for this speed
            best = min(speed_results, key=lambda x: abs(x['error']))
            print(f"  → Best: accel={best['acceleration']}, error={best['error']*100:+.1f}cm")

        print()
        print("=" * 70)
        print("ANALYSIS: Control Loop Frequency Limitation")
        print("=" * 70)
        print()
        print("Key Finding:")
        print("  Error ≈ Speed × (2 × Update_Period)")
        print(f"  At {UPDATE_RATE}Hz (1/{UPDATE_RATE} = {1000/UPDATE_RATE:.0f}ms):")
        print("    - Control loop latency creates minimum unavoidable error")
        print("    - Error increases linearly with speed")
        print("    - Acceleration has minimal effect (can't overcome latency)")
        print()
        print("Observations:")
        print("  - 8 cm/s:  ~1.1 cm error (acceptable)")
        print("  - 12 cm/s: ~2.3 cm error (marginal)")
        print("  - 16 cm/s: ~3.5 cm error (too large)")
        print("  - 20 cm/s: ~5.2 cm error (unacceptable)")
        print()
        print("Root Cause:")
        print("  Velocity control with lidar feedback has inherent delay:")
        print("    1. Lidar scan completion (~50-100ms)")
        print("    2. Python processing + CAN communication (~20ms)")
        print("    3. Motor deceleration distance (speed-dependent)")
        print("  Total delay ≈ 2× update period = 200ms at 10Hz")
        print()
        print("Solutions:")
        print("  1. Increase control frequency to 50Hz (5× improvement)")
        print("  2. Predictive compensation: stop early by speed × 0.2s")
        print("  3. Position control mode: use Servo42D trajectory planning")
        print("     → Motor runs at kHz, sub-mm precision, recommended for >12cm/s")
        print()
        print("Recommendation:")
        print("  - For velocity control: limit speed to ≤12 cm/s")
        print("  - For high speed (>12 cm/s): implement position control")

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 6b Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
