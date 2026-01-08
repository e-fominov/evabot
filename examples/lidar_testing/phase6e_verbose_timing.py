#!/usr/bin/env python3
"""
Phase 6e: Verbose Timing Analysis - Single Speed, Multiple Iterations

Runs 10 iterations of square pattern at single speed with detailed timestamp logging
to identify where time is being spent (especially the ~0.5s pauses).

Usage:
    robot run examples/lidar_testing/phase6e_verbose_timing.py
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1


def log(msg, t0=None):
    """Print message with timestamp."""
    if t0 is not None:
        elapsed = (time.time() - t0) * 1000  # milliseconds
        print(f"[+{elapsed:6.1f}ms] {msg}")
    else:
        print(f"[{time.time():.3f}] {msg}")


def align_to_wall(robot, wall_angle, max_iterations=50):
    """Align robot parallel to a wall with timing logs."""
    ALIGNMENT_THRESHOLD = 3.0
    ROTATION_GAIN = 0.02
    MAX_ROTATION_SPEED = 0.3
    UPDATE_RATE = 5

    t0 = time.time()
    log(f"  Starting alignment to {wall_angle}°...", t0)

    for iteration in range(max_iterations):
        t_iter = time.time()
        distance, angle_deg, quality = robot.lidar.check_wall(wall_angle)
        log(f"    Iter {iteration}: check_wall({wall_angle}°) → angle={angle_deg:+.2f}° (quality={quality:.2f})" if angle_deg is not None else f"    Iter {iteration}: check_wall({wall_angle}°) → None", t_iter)

        if angle_deg is not None and abs(angle_deg) < ALIGNMENT_THRESHOLD:
            robot.drive.halt()
            log(f"  ✓ Aligned! Final angle: {angle_deg:+.2f}°", t0)
            return True

        if angle_deg is not None:
            rotation_speed = ROTATION_GAIN * angle_deg
            rotation_speed = max(-MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, rotation_speed))
            robot.drive.move(vtheta=rotation_speed)
            log(f"    → drive.move(vtheta={rotation_speed:+.3f})", t_iter)

        time.sleep(1.0 / UPDATE_RATE)

    robot.drive.halt()
    log(f"  ✗ Alignment timeout after {max_iterations} iterations", t0)
    return False


def move_to_wall_position_control(robot, target_wall_angle, target_distance=0.17,
                                   speed=0.50, update_rate=50):
    """
    Move toward wall using position control with verbose timing.

    Args:
        robot: Robot instance
        target_wall_angle: Wall to approach (0=front, 90=right, 180=back, 270=left)
        target_distance: Target distance from wall (m)
        speed: Movement speed (m/s)
        update_rate: Control loop frequency (Hz)

    Returns:
        (success, final_distance, min_distance)
    """
    t0 = time.time()
    log(f"  Moving → wall {target_wall_angle}° @ {speed*100:.0f}cm/s", t0)

    # Determine movement direction from wall angle
    direction_map = {
        0: (1, 0, 0),    # front: +x
        90: (0, -1, 0),  # right: -y
        180: (-1, 0, 0), # back: -x
        270: (0, 1, 0),  # left: +y
    }
    vx_dir, vy_dir, vtheta_dir = direction_map.get(target_wall_angle, (0, 0, 0))

    update_count = 0
    min_wall_distance = float('inf')
    lost_measurement_count = 0
    max_lost_measurements = 5

    last_log_time = t0
    LOG_INTERVAL = 0.5  # Log every 0.5s during movement

    while time.time() - t0 < 15.0:  # 15s timeout
        t_iter = time.time()

        # Measure wall distance
        wall_distance, _, _ = robot.lidar.check_wall(target_wall_angle)

        if wall_distance is None:
            lost_measurement_count += 1
            if lost_measurement_count >= max_lost_measurements:
                log(f"  ✗ Lost wall measurement ({max_lost_measurements} consecutive failures)", t0)
                robot.drive.halt()
                return False, None, min_wall_distance
            time.sleep(1.0 / update_rate)
            continue
        else:
            lost_measurement_count = 0

        # Track minimum distance
        if wall_distance < min_wall_distance:
            min_wall_distance = wall_distance

        # Calculate remaining distance
        remaining = wall_distance - target_distance

        # Periodic logging during movement
        if t_iter - last_log_time >= LOG_INTERVAL:
            log(f"    wall_dist={wall_distance*100:.1f}cm, remaining={remaining*100:.1f}cm, updates={update_count}", t0)
            last_log_time = t_iter

        if remaining <= 0.005:  # Within 5mm, stop
            log(f"  → drive.halt() [remaining={remaining*100:.1f}cm < 0.5cm]", t0)
            robot.drive.halt()
            log(f"  Waiting 0.3s for full stop...", t0)
            time.sleep(0.3)
            log(f"  Stop complete", t0)
            break

        # Set position target
        robot.drive.set_target_position(
            dx=remaining * vx_dir,
            dy=remaining * vy_dir,
            dtheta=0,
            speed=speed
        )
        update_count += 1

        time.sleep(1.0 / update_rate)

    # Measure final distance
    t_final = time.time()
    log(f"  Measuring final distance...", t0)
    final_distance, _, _ = robot.lidar.check_wall(target_wall_angle)
    log(f"    check_wall({target_wall_angle}°) → {final_distance*100:.1f}cm" if final_distance else "    check_wall() → None", t0)

    if final_distance is None:
        log(f"  ✗ Could not measure final distance", t0)
        return False, None, min_wall_distance

    error = final_distance - target_distance
    elapsed = time.time() - t0

    log(f"  ✓ Reached wall: {final_distance*100:.1f}cm (error: {error*100:+.1f}cm, {elapsed:.2f}s, {update_count} updates)", t0)
    return True, final_distance, min_wall_distance


def run_square_iteration(robot, speed, iteration_num):
    """Run one square pattern iteration with detailed timing."""
    print()
    print("=" * 70)
    print(f"ITERATION {iteration_num} @ {speed*100:.0f} cm/s")
    print("=" * 70)

    t_iteration = time.time()

    movements = [
        (0, "Forward → Front"),
        (270, "Left → Left"),
        (180, "Backward → Back"),
        (90, "Right → Right"),
    ]

    for i, (wall_angle, description) in enumerate(movements, 1):
        print()
        print(f"[{i}/4] {description} Wall ({wall_angle}°)")
        print("-" * 70)

        t_movement = time.time()

        # Move to wall
        success, final_distance, min_distance = move_to_wall_position_control(
            robot, wall_angle, target_distance=0.17, speed=speed, update_rate=50
        )

        if not success:
            print(f"  ✗ Movement failed")
            return False

        # Check alignment
        t_align_check = time.time()
        log(f"  Checking alignment...", t_align_check)
        _, angle_deg, _ = robot.lidar.check_wall(wall_angle)
        log(f"    check_wall({wall_angle}°) → angle={angle_deg:+.2f}°" if angle_deg is not None else "    check_wall() → None", t_align_check)

        if angle_deg is not None and abs(angle_deg) < 3.0:
            log(f"  ✓ Already aligned (angle={angle_deg:+.2f}°), skipping", t_align_check)
        else:
            log(f"  Alignment needed (angle={angle_deg:+.2f}°)", t_align_check)
            if not align_to_wall(robot, wall_angle):
                print(f"  ✗ Alignment failed")
                return False

        elapsed = time.time() - t_movement
        log(f"Movement {i}/4 complete: {elapsed:.2f}s", t_movement)

    total_time = time.time() - t_iteration
    print()
    print(f"Iteration {iteration_num} complete: {total_time:.2f}s")

    return True


def main():
    print("=" * 70)
    print("Phase 6e: Verbose Timing Analysis")
    print("=" * 70)
    print()
    print("Testing: 10 iterations at 100 cm/s")
    print("Output: Detailed timestamp logging for each operation")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Test parameters
    TEST_SPEED = 1.00  # 100 cm/s
    NUM_ITERATIONS = 10

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X', acceleration=100)
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    try:
        for iteration in range(1, NUM_ITERATIONS + 1):
            success = run_square_iteration(robot, TEST_SPEED, iteration)
            if not success:
                print(f"✗ Iteration {iteration} failed, stopping test")
                break

            # Small delay between iterations
            if iteration < NUM_ITERATIONS:
                print()
                print(f"Waiting 1s before next iteration...")
                time.sleep(1.0)

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 6e Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
