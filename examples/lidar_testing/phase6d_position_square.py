#!/usr/bin/env python3
"""
Phase 6d: High-Speed Square Pattern with Position Control

Uses the new position control system to complete square pattern at high speeds.

Previous Results:
- Phase 6 (velocity control): Safe only at ≤12 cm/s, collisions at 16+ cm/s
- Phase 6c (position control): 2-4× better accuracy at high speeds, no oscillations

This test applies position control to the full square pattern to achieve:
- Safe navigation at 16-24 cm/s
- Faster completion times
- Better stopping accuracy
- No collisions

Test Strategy:
1. Move forward using position control + lidar monitoring
2. Stop when reaching target distance from wall
3. Align if needed (conditional)
4. Repeat for all 4 sides
5. Return to center

Comparison Goals:
╔═══════════╦═══════════════════╦═══════════════════╗
║  Speed    ║ Velocity (Phase 6)║ Position (Phase 6d)║
╠═══════════╬═══════════════════╬═══════════════════╣
║  8 cm/s   ║  ✓ Safe (~40s)    ║  ✓ Safe (~40s)    ║
║ 12 cm/s   ║  ✓ Safe (~27s)    ║  ✓ Safe (~27s)    ║
║ 16 cm/s   ║  ✗ Collisions     ║  ✓ Safe (~20s)?   ║
║ 20 cm/s   ║  ✗ Collisions     ║  ✓ Safe (~16s)?   ║
║ 24 cm/s   ║  ✗ Not tested     ║  ✓ Safe (~13s)?   ║
╚═══════════╩═══════════════════╩═══════════════════╝

Usage:
    robot run examples/lidar_testing/phase6d_position_square.py
"""

import time
import math
from evabot import Robot, MecanumDrive, RPLidarC1


def move_to_center(robot, arena_size=0.60, max_retries=3):
    """Move to arena center using velocity control (low speed, safe)."""
    print("Moving to center...")

    # Retry wall measurements if needed (lidar needs time to accumulate scan data)
    front_distance = None
    back_distance = None
    left_distance = None
    right_distance = None

    for attempt in range(max_retries):
        # Measure current position
        front_distance, _, _ = robot.lidar.check_wall(0)
        back_distance, _, _ = robot.lidar.check_wall(180)
        left_distance, _, _ = robot.lidar.check_wall(270)
        right_distance, _, _ = robot.lidar.check_wall(90)

        # Debug: show all measurements
        if attempt == 0:
            print(f"  Wall measurements (attempt {attempt+1}):")
        else:
            print(f"  Retry {attempt}: Wall measurements:")
        print(
            f"    Front (0°):   {front_distance*100:.1f}cm"
            if front_distance
            else "    Front (0°):   None"
        )
        print(
            f"    Right (90°):  {right_distance*100:.1f}cm"
            if right_distance
            else "    Right (90°):  None"
        )
        print(
            f"    Back (180°):  {back_distance*100:.1f}cm"
            if back_distance
            else "    Back (180°):  None"
        )
        print(
            f"    Left (270°):  {left_distance*100:.1f}cm"
            if left_distance
            else "    Left (270°):  None"
        )

        # Check if we have minimum required measurements
        if front_distance and back_distance:
            print(f"  ✓ Got required wall measurements")
            break

        if attempt < max_retries - 1:
            print(f"  ⚠ Missing wall data, waiting for more scans...")
            time.sleep(1.0)

    if not (front_distance and back_distance):
        print("  ✗ Cannot determine position (need front & back walls)")
        return False

    # Calculate required movement
    target_distance = arena_size / 2
    move_x = front_distance - target_distance
    move_y = (left_distance - target_distance) if left_distance else 0.0

    print(f"  Required movement: Δx={move_x*100:.1f}cm, Δy={move_y*100:.1f}cm")

    if abs(move_x) > 0.02 or abs(move_y) > 0.02:
        distance = (move_x**2 + move_y**2) ** 0.5
        move_time = distance / 0.08  # 8cm/s for safety

        if distance > 0:
            vx = (move_x / distance) * 0.08
            vy = (move_y / distance) * 0.08
            robot.drive.move(vx=vx, vy=vy)
            time.sleep(move_time)
            robot.drive.halt()
            time.sleep(0.2)

        print("  ✓ Centered")
    else:
        print("  ✓ Already centered")

    return True


def check_and_align_if_needed(robot, wall_angle, threshold=3.0, max_iterations=50):
    """Check alignment and only align if error exceeds threshold."""
    ALIGNMENT_THRESHOLD = 2.0
    ROTATION_GAIN = 0.02
    MAX_ROTATION_SPEED = 0.3
    UPDATE_RATE = 5

    # Check current alignment
    distance, angle_deg, quality = robot.lidar.check_wall(wall_angle)

    if angle_deg is None:
        print(f"  ✗ Cannot measure wall {wall_angle}°")
        return False

    print(f"  Alignment: {angle_deg:+.2f}° (threshold: ±{threshold}°)")

    if abs(angle_deg) < threshold:
        print(f"  ✓ Already aligned, skipping")
        return True

    # Need alignment
    print(f"  Aligning to wall {wall_angle}°...")

    for _ in range(max_iterations):
        distance, angle_deg, quality = robot.lidar.check_wall(wall_angle)

        if angle_deg is not None and abs(angle_deg) < ALIGNMENT_THRESHOLD:
            robot.drive.halt()
            print(f"  ✓ Aligned! angle: {angle_deg:+.2f}°")
            return True

        if angle_deg is not None:
            rotation_speed = ROTATION_GAIN * angle_deg
            rotation_speed = max(
                -MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, rotation_speed)
            )
            robot.drive.move(vtheta=rotation_speed)

        time.sleep(1.0 / UPDATE_RATE)

    robot.drive.halt()
    print(f"  ✗ Could not align")
    return False


def move_to_wall_position_control(
    robot,
    dx: float = 0,
    dy: float = 0,
    target_wall_angle: int = 0,
    target_distance: float = 0.17,
    speed: float = 0.2,
    update_rate: int = 50,
):
    """
    Move toward wall using position control with continuous lidar monitoring.

    Uses set_target_position() and updates target based on lidar distance.
    This eliminates the speed-dependent error of velocity control.

    Args:
        robot: Robot instance
        dx, dy: Initial movement direction (ignored if 0, uses lidar)
        target_wall_angle: Wall to approach
        target_distance: Stop at this distance from wall (m)
        speed: Movement speed (m/s)
        update_rate: Control loop frequency (Hz)

    Returns:
        tuple: (success, final_distance, min_distance_to_any_wall)
    """
    direction_name = ""
    if dx > 0:
        direction_name = "forward"
    elif dx < 0:
        direction_name = "backward"
    elif dy > 0:
        direction_name = "left"
    elif dy < 0:
        direction_name = "right"

    print(
        f"  Moving {direction_name} → wall {target_wall_angle}° (position control @ {speed*100:.0f}cm/s)"
    )

    start_time = time.time()
    min_wall_distance = float("inf")
    update_count = 0
    stopped = False

    lost_measurement_count = 0
    max_lost_measurements = (
        5  # Allow up to 5 consecutive failed readings before giving up
    )

    while time.time() - start_time < 15.0:  # 15s timeout
        # Measure distance to target wall
        wall_distance, _, _ = robot.lidar.check_wall(target_wall_angle)

        if wall_distance is None:
            lost_measurement_count += 1
            if lost_measurement_count >= max_lost_measurements:
                print(
                    f"    ✗ Lost wall measurement ({max_lost_measurements} consecutive failures)"
                )
                robot.drive.halt()
                return False, None, min_wall_distance
            # Skip this cycle but keep moving
            time.sleep(1.0 / update_rate)
            continue
        else:
            lost_measurement_count = 0  # Reset counter on successful reading

        # Track minimum distance to ALL walls for collision detection
        for angle in [0, 90, 180, 270]:
            d, _, _ = robot.lidar.check_wall(angle)
            if d is not None:
                min_wall_distance = min(min_wall_distance, d)

        # Check if reached target
        remaining = wall_distance - target_distance

        if remaining <= 0.005:  # Within 5mm
            robot.drive.halt()
            stopped = True
            break

        # POSITION CONTROL: Set target based on remaining distance
        # Motor handles trajectory planning at kHz
        # Need to preserve direction: dx>0 = forward, dx<0 = backward
        if dx > 0:
            robot.drive.set_target_position(dx=remaining, speed=speed)
        elif dx < 0:
            robot.drive.set_target_position(dx=-remaining, speed=speed)
        elif dy > 0:
            robot.drive.set_target_position(dy=remaining, speed=speed)
        elif dy < 0:
            robot.drive.set_target_position(dy=-remaining, speed=speed)

        update_count += 1
        time.sleep(1.0 / update_rate)

    if not stopped:
        robot.drive.halt()
        print(f"    ✗ Timeout")
        return False, None, min_wall_distance

    # Wait for full stop
    time.sleep(0.2)

    # Measure final distance
    final_distance, _, _ = robot.lidar.check_wall(target_wall_angle)
    elapsed = time.time() - start_time

    if final_distance:
        error = final_distance - target_distance
        print(
            f"  ✓ Reached wall: {final_distance*100:.1f}cm (error: {error*100:+.1f}cm, {elapsed:.2f}s, {update_count} updates)"
        )
        return True, final_distance, min_wall_distance
    else:
        print(f"  ✗ Cannot measure final distance")
        return False, None, min_wall_distance


def run_square_pattern(robot, speed, target_distance=0.17, alignment_threshold=3.0):
    """
    Run square pattern at specified speed using position control.

    Returns:
        dict: Results with timing, errors, collisions
    """
    print()
    print("─" * 70)
    print(f"Square Pattern @ {speed*100:.0f} cm/s (Position Control)")
    print("─" * 70)

    start_time = time.time()
    all_distances = []
    all_errors = []
    min_distance_overall = float("inf")
    alignments_performed = 0

    # Step 1: Forward to front wall
    print("\n[1/4] Forward → Front Wall (0°)")
    success, final_dist, min_dist = move_to_wall_position_control(
        robot, dx=1.0, target_wall_angle=0, target_distance=target_distance, speed=speed
    )
    if not success:
        return None
    all_distances.append(final_dist)
    all_errors.append(final_dist - target_distance)
    min_distance_overall = min(min_distance_overall, min_dist)

    time.sleep(0.3)
    if check_and_align_if_needed(robot, 0, threshold=alignment_threshold):
        alignments_performed += 1
    time.sleep(0.3)

    # Step 2: Left to left wall
    print("\n[2/4] Left → Left Wall (270°)")
    success, final_dist, min_dist = move_to_wall_position_control(
        robot,
        dy=1.0,
        target_wall_angle=270,
        target_distance=target_distance,
        speed=speed,
    )
    if not success:
        return None
    all_distances.append(final_dist)
    all_errors.append(final_dist - target_distance)
    min_distance_overall = min(min_distance_overall, min_dist)

    time.sleep(0.3)
    if check_and_align_if_needed(robot, 270, threshold=alignment_threshold):
        alignments_performed += 1
    time.sleep(0.3)

    # Step 3: Backward to back wall
    print("\n[3/4] Backward → Back Wall (180°)")
    success, final_dist, min_dist = move_to_wall_position_control(
        robot,
        dx=-1.0,
        target_wall_angle=180,
        target_distance=target_distance,
        speed=speed,
    )
    if not success:
        return None
    all_distances.append(final_dist)
    all_errors.append(final_dist - target_distance)
    min_distance_overall = min(min_distance_overall, min_dist)

    time.sleep(0.3)
    if check_and_align_if_needed(robot, 180, threshold=alignment_threshold):
        alignments_performed += 1
    time.sleep(0.3)

    # Step 4: Right to right wall
    print("\n[4/4] Right → Right Wall (90°)")
    success, final_dist, min_dist = move_to_wall_position_control(
        robot,
        dy=-1.0,
        target_wall_angle=90,
        target_distance=target_distance,
        speed=speed,
    )
    if not success:
        return None
    all_distances.append(final_dist)
    all_errors.append(final_dist - target_distance)
    min_distance_overall = min(min_distance_overall, min_dist)

    time.sleep(0.3)
    if check_and_align_if_needed(robot, 90, threshold=alignment_threshold):
        alignments_performed += 1

    elapsed = time.time() - start_time

    # Calculate metrics
    max_error = max([abs(e) for e in all_errors])
    collision = min_distance_overall < 0.13

    return {
        "speed": speed,
        "time": elapsed,
        "distances": all_distances,
        "errors": all_errors,
        "max_error": max_error,
        "min_distance": min_distance_overall,
        "collision": collision,
        "alignments": alignments_performed,
    }


def main():
    print("=" * 70)
    print("Phase 6d: High-Speed Square Pattern (Position Control)")
    print("=" * 70)
    print()
    print("This test uses position control to enable safe high-speed navigation.")
    print()
    print("Expected improvements over velocity control:")
    print("  - 16-24 cm/s: Safe execution (was collision-prone)")
    print("  - 2-4× better stopping accuracy at high speeds")
    print("  - Faster completion times")
    print()
    print("Test speeds: 8, 12, 16, 20, 24 cm/s")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Test parameters
    TEST_SPEEDS = [0.40, 0.50, 0.75, 1.0]  # m/s
    # TEST_SPEEDS = [0.24, 0.30, 0.35, 0.40]  # m/s
    # TEST_SPEEDS = [0.08, 0.12, 0.16, 0.20, 0.24, 0.30, 0.35, 0.40]  # m/s
    TARGET_DISTANCE = 0.17  # 17cm from wall
    ALIGNMENT_THRESHOLD = 3.0  # Only align if error > 3°
    ACCELERATION = 10

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(
        fl=3, fr=4, bl=1, br=2, pattern="X", acceleration=ACCELERATION
    )
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    all_results = []

    try:
        for speed in TEST_SPEEDS:
            # Move to center before each test
            print()
            print("=" * 70)
            if not move_to_center(robot):
                print("  ✗ Failed to center, skipping")
                continue

            time.sleep(0.5)

            # Run square pattern
            result = run_square_pattern(
                robot, speed, TARGET_DISTANCE, ALIGNMENT_THRESHOLD
            )

            if result:
                all_results.append(result)

            time.sleep(1.0)

        # Display results
        print()
        print()
        print("=" * 70)
        print("HIGH-SPEED SQUARE PATTERN RESULTS")
        print(f"ACCELERATION = {ACCELERATION}")
        print("=" * 70)
        print()

        if all_results:
            print(
                f"{'Speed':>8} │ {'Time':>7} │ {'Max Err':>8} │ {'Min Dist':>9} │ {'Collision':>10} │ {'Aligns':>7}"
            )
            print("─" * 70)

            for r in all_results:
                speed_str = f"{r['speed']*100:.0f} cm/s"
                time_str = f"{r['time']:.1f}s"
                err_str = f"{r['max_error']*100:.1f}cm"
                min_str = f"{r['min_distance']*100:.1f}cm"
                coll_str = "✗ YES" if r["collision"] else "✓ No"
                align_str = f"{r['alignments']}/4"

                print(
                    f"{speed_str:>8} │ {time_str:>7} │ {err_str:>8} │ {min_str:>9} │ {coll_str:>10} │ {align_str:>7}"
                )

        print()
        print("=" * 70)
        print("ANALYSIS")
        print("=" * 70)
        print()
        print("Success Criteria:")
        print("  ✓ No collisions (min distance ≥ 13cm)")
        print("  ✓ Max error < 3cm")
        print("  ✓ Faster than velocity control")
        print()

        if all_results:
            successful_speeds = [
                r for r in all_results if not r["collision"] and r["max_error"] < 0.03
            ]
            if successful_speeds:
                fastest = min(successful_speeds, key=lambda x: x["time"])
                print(
                    f"Best Result: {fastest['speed']*100:.0f} cm/s in {fastest['time']:.1f}s"
                )
                print(f"  Max error: {fastest['max_error']*100:.1f}cm")
                print(f"  Min distance: {fastest['min_distance']*100:.1f}cm")
                print(f"  Alignments: {fastest['alignments']}/4")

                # Compare with velocity control baseline
                if fastest["speed"] >= 0.16:
                    print()
                    print("🎉 HIGH-SPEED SUCCESS!")
                    print(
                        f"  Position control enables safe {fastest['speed']*100:.0f} cm/s navigation"
                    )
                    print(f"  Velocity control: Collisions at 16+ cm/s")

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 6d Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
