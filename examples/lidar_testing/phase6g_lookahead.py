#!/usr/bin/env python3
"""
Phase 6g: Lookahead Control for Wall Following

Uses the new lookahead-based position control for continuous alignment.
Much simpler than phase6f - just pass angle_error directly to set_target_position()!

The lookahead controller (in mecanum.py) handles:
- Independent linear and angular velocities
- Proportional slowdown as approaching target
- Immediate rotation response via K_angular gain

Usage:
    robot run examples/lidar_testing/phase6g_lookahead.py
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


def move_to_wall_with_lookahead(
    robot,
    target_wall_angle,
    target_distance=0.17,
    speed=0.70,
    update_rate=10,
):
    """
    Move toward wall using lookahead position control with continuous alignment.

    The lookahead controller automatically handles:
    - Linear velocity proportional to remaining distance (K_linear gain)
    - Angular velocity proportional to angle error (K_angular gain)
    - Short lookahead window (100ms) for immediate response
    - Re-planning every 20ms based on current state

    Args:
        robot: Robot instance
        target_wall_angle: Wall to approach (0=front, 90=right, 180=back, 270=left)
        target_distance: Target distance from wall (m)
        speed: Maximum movement speed (m/s)
        update_rate: Control loop frequency (Hz)

    Returns:
        (success, final_distance, final_angle)
    """
    # Determine movement direction
    direction_map = {
        0: (1, 0),  # front: +x
        90: (0, -1),  # right: -y
        180: (-1, 0),  # back: -x
        270: (0, 1),  # left: +y
    }
    vx_dir, vy_dir = direction_map.get(target_wall_angle, (0, 0))

    start_time = time.time()
    update_count = 0
    last_log_time = start_time
    LOG_INTERVAL = 0.2

    log(f"  Moving → wall {target_wall_angle}° @ {speed*100:.0f}cm/s", start_time)

    while time.time() - start_time < 15.0:  # 15s timeout
        t_iter = time.time()

        # Measure wall distance and angle
        wall_distance, angle_error, quality = robot.lidar.check_wall(target_wall_angle)

        if wall_distance is None:
            if t_iter - last_log_time >= LOG_INTERVAL:
                log(f"    ✗ check_wall() → None (update {update_count})", start_time)
                last_log_time = t_iter
            # Lost lidar reading, halt
            robot.drive.halt()
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
            break

        # Calculate target position
        dx = remaining * vx_dir
        dy = remaining * vy_dir

        # Use angle_error directly for alignment (only if quality is good)
        dtheta_deg = 0.0
        if angle_error is not None and quality is not None and quality > 0.5:
            dtheta_deg = angle_error  # Direct angle error!
            # The lookahead controller's K_angular gain will handle the rotation rate

        # Periodic logging
        if t_iter - last_log_time >= LOG_INTERVAL:
            log(
                f"    dist={wall_distance*100:.1f}cm, remaining={remaining*100:.1f}cm, "
                f"angle_err={angle_error:+.2f}°, target_dtheta={dtheta_deg:+.2f}°, "
                f"q={quality:.2f}, updates={update_count}",
                start_time,
            )
            last_log_time = t_iter

        # Set position target (lookahead controller handles the rest!)
        robot.drive.set_target_position(
            dx=dx,
            dy=dy,
            dtheta_deg=dtheta_deg,
            speed=speed,
        )
        update_count += 1

        time.sleep(1.0 / update_rate)

    # Measure final state
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
    """Run one square pattern iteration with lookahead control."""
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

        # Move to wall with lookahead control
        success, final_distance, final_angle = move_to_wall_with_lookahead(
            robot, wall_angle, target_distance=0.17, speed=speed, update_rate=10
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
    print("Phase 6g: Lookahead Control for Wall Following")
    print("=" * 70)
    print()
    print("New approach:")
    print("  - Uses lookahead position control from mecanum.py")
    print("  - K_linear=0.5 for position control (slows as approaching)")
    print("  - K_angular=1.0 for rotation (immediate response)")
    print("  - 100ms lookahead window, re-planned every 20ms")
    print()
    print("Testing: 3 iterations at 30 cm/s")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    # Test parameters
    TEST_SPEED = 0.3  # 30 cm/s
    NUM_ITERATIONS = 3

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern="X", acceleration=1)
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
        print(f"Completed: {len(iteration_times)}/{NUM_ITERATIONS} iterations")
        print(f"Average time: {avg_time:.2f}s")
        print(f"Best time:    {min_time:.2f}s")
        print(f"Worst time:   {max_time:.2f}s")
        print()
        print("Comparison:")
        print(f"  Phase 6d (basic position control):  ~8.2s")
        print(f"  Phase 6g (lookahead control):       {avg_time:.2f}s")
        if avg_time < 8.2:
            print(
                f"  Improvement:                         {8.2 - avg_time:.2f}s ({(8.2-avg_time)/8.2*100:.1f}%)"
            )

    print()
    print("=" * 70)
    print("Phase 6g Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
