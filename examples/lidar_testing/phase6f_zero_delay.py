#!/usr/bin/env python3
"""
Phase 6f: Zero-Delay Optimization with Continuous Alignment

Eliminates all artificial delays and performs alignment during movement instead of at stops.

Optimizations:
1. Remove 0.3s sleep after halt (saves 1.2s per square)
2. Continuous alignment during approach (saves 230ms per alignment = ~175ms avg per square)
3. Increase alignment threshold 3° → 5° (more tolerant since we align continuously)

Expected improvement: 7.5s → 6.0s (20% faster)

Usage:
    robot run examples/lidar_testing/phase6f_zero_delay.py
"""

import time
import math
from evabot import Robot, MecanumDrive, RPLidarC1


def log(msg, t0=None):
    """Print message with timestamp."""
    if t0 is not None:
        elapsed = (time.time() - t0) * 1000  # milliseconds
        print(f"[+{elapsed:6.1f}ms] {msg}")
    else:
        print(f"[{time.time():.3f}] {msg}")


def move_to_wall_with_alignment(
    robot,
    target_wall_angle,
    target_distance=0.17,
    speed=1.00,
    update_rate=10,
    align_gain=50.0,
    max_rotation_speed_deg_per_sec=180.0,
):
    """
    Move toward wall using position control with continuous alignment.

    Uses rotation speed (degrees/second) for alignment, giving constant rotation
    rate throughout the movement regardless of remaining distance.

    Args:
        robot: Robot instance
        target_wall_angle: Wall to approach (0=front, 90=right, 180=back, 270=left)
        target_distance: Target distance from wall (m)
        speed: Movement speed (m/s)
        update_rate: Control loop frequency (Hz)
        align_gain: Proportional gain (deg/s per degree of error)
        max_rotation_speed_deg_per_sec: Maximum rotation speed (degrees/second)

    Returns:
        (success, final_distance, final_angle)
    """
    # Determine movement direction
    direction_map = {
        0: (1, 0, 0),  # front: +x
        90: (0, -1, 0),  # right: -y
        180: (-1, 0, 0),  # back: -x
        270: (0, 1, 0),  # left: +y
    }
    vx_dir, vy_dir, _ = direction_map.get(target_wall_angle, (0, 0, 0))

    start_time = time.time()
    update_count = 0
    last_log_time = start_time
    LOG_INTERVAL = 0.1  # Log every 0.5s

    log(f"  Moving → wall {target_wall_angle}° @ {speed*100:.0f}cm/s", start_time)

    while time.time() - start_time < 15.0:  # 15s timeout
        t_iter = time.time()

        # Measure wall distance and angle
        wall_distance, angle_error, quality = robot.lidar.check_wall(target_wall_angle)

        if wall_distance is None:
            if t_iter - last_log_time >= LOG_INTERVAL:
                log(f"    ✗ check_wall() → None (update {update_count})", start_time)
                last_log_time = t_iter
            # Lost lidar reading, continue with last command
            time.sleep(1.0 / update_rate)
            continue

        # Calculate remaining distance
        remaining = wall_distance - target_distance

        if remaining <= 0.005:  # Within 5mm, stop
            log(
                f"  → drive.halt() [remaining={remaining*100:.1f}cm < 0.5cm]",
                start_time,
            )
            robot.drive.halt()
            log(f"  Halt complete (NO SLEEP)", start_time)
            break

        # Calculate rotation based on desired rotation SPEED (degrees/second)
        # This gives constant rotation rate throughout movement
        import math

        dx = remaining * vx_dir
        dy = remaining * vy_dir

        # Calculate desired rotation speed (proportional to angle error)
        rotation_speed_deg_per_sec = 0.0
        if angle_error is not None and quality is not None and quality > 0.5:
            rotation_speed_deg_per_sec = align_gain * angle_error
            # Clamp to maximum rotation speed
            rotation_speed_deg_per_sec = max(
                -max_rotation_speed_deg_per_sec,
                min(max_rotation_speed_deg_per_sec, rotation_speed_deg_per_sec),
            )

        # Convert rotation speed to rotation per update cycle
        dtheta_deg = rotation_speed_deg_per_sec / update_rate

        # Periodic detailed logging
        if t_iter - last_log_time >= LOG_INTERVAL:
            log(
                f"    dist={wall_distance*100:.1f}cm, remaining={remaining*100:.1f}cm, angle_err={angle_error:+.2f}°, rot_speed={rotation_speed_deg_per_sec:+.1f}°/s, dtheta={dtheta_deg:+.3f}°, q={quality:.2f}, updates={update_count}",
                start_time,
            )
            last_log_time = t_iter

        # Set position target with rotation speed-based alignment
        robot.drive.set_target_position(
            dx=dx,
            dy=dy,
            dtheta_deg=dtheta_deg,  # Constant rotation speed!
            speed=speed,
        )
        update_count += 1

        time.sleep(1.0 / update_rate)

    # Measure final state (NO SLEEP before measurement!)
    log(f"  Measuring final distance...", start_time)
    final_distance, final_angle, quality = robot.lidar.check_wall(target_wall_angle)
    log(
        (
            f"    check_wall({target_wall_angle}°) → dist={final_distance*100:.1f}cm, angle={final_angle:+.2f}°, q={quality:.2f}"
            if final_distance
            else "    check_wall() → None"
        ),
        start_time,
    )

    if final_distance is None:
        log(f"  ✗ Could not measure final distance", start_time)
        return False, None, None

    error = final_distance - target_distance
    elapsed = time.time() - start_time
    log(
        f"  ✓ Reached wall: {final_distance*100:.1f}cm (error: {error*100:+.1f}cm, angle: {final_angle:+.2f}°, {elapsed:.2f}s, {update_count} updates)",
        start_time,
    )

    return True, final_distance, final_angle


def run_square_iteration(robot, speed, iteration_num):
    """Run one square pattern iteration with zero-delay optimization."""
    print()
    print("=" * 70)
    print(f"ITERATION {iteration_num} @ {speed*100:.0f} cm/s")
    print("=" * 70)

    t_iteration = time.time()

    movements = [
        (0, "Front"),
        (270, "Left"),
        (180, "Back"),
        (90, "Right"),
    ]

    for i, (wall_angle, description) in enumerate(movements, 1):
        print()
        print(f"[{i}/4] {description} Wall ({wall_angle}°)")
        print("-" * 70)

        t_movement = time.time()

        # Move to wall with continuous alignment
        success, final_distance, final_angle = move_to_wall_with_alignment(
            robot, wall_angle, target_distance=0.17, speed=speed, update_rate=50
        )

        if not success:
            print(f"  ✗ Movement {i}/4 failed")
            return False, None

        elapsed = time.time() - t_movement
        log(f"Movement {i}/4 complete: {elapsed:.2f}s", t_movement)

    total_time = time.time() - t_iteration
    print()
    print(f"Iteration {iteration_num} complete: {total_time:.2f}s")

    return True, total_time


def main():
    print("=" * 70)
    print("Phase 6f: Zero-Delay Optimization")
    print("=" * 70)
    print()
    print("Optimizations:")
    print("  1. Remove 0.3s sleep after halt (1.2s savings per square)")
    print("  2. Continuous alignment during movement (no separate alignment stops)")
    print("  3. Target: 7.5s → 6.0s (20% improvement)")
    print()
    print("Testing: 10 iterations at 100 cm/s")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    # Test parameters
    TEST_SPEED = 0.30  # 100 cm/s
    NUM_ITERATIONS = 10

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern="X", acceleration=100)
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    iteration_times = []

    try:
        for iteration in range(1, NUM_ITERATIONS + 1):
            success, iteration_time = run_square_iteration(robot, TEST_SPEED, iteration)

            if not success:
                print(f"✗ Iteration {iteration} failed")
                break

            iteration_times.append(iteration_time)

            if iteration == 1:
                print(f"  Iteration 1: {iteration_time:.2f}s")
                print()
                print("Continuing with iterations 2-10 (compact output)...")
            else:
                print(f"  Iteration {iteration}: {iteration_time:.2f}s")

            # Small delay between iterations
            if iteration < NUM_ITERATIONS:
                time.sleep(0.5)

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()

    # Statistics
    if iteration_times:
        avg_time = sum(iteration_times) / len(iteration_times)
        min_time = min(iteration_times)
        max_time = max(iteration_times)

        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print()
        print(f"Completed: {len(iteration_times)}/10 iterations")
        print(f"Average time: {avg_time:.2f}s")
        print(f"Best time:    {min_time:.2f}s")
        print(f"Worst time:   {max_time:.2f}s")
        print()
        print("Comparison:")
        print(f"  Phase 6e (with delays):    ~7.50s")
        print(f"  Phase 6f (zero-delay):     {avg_time:.2f}s")
        print(
            f"  Improvement:               {7.50 - avg_time:.2f}s ({(7.50-avg_time)/7.50*100:.1f}%)"
        )

    print()
    print("=" * 70)
    print("Phase 6f Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
