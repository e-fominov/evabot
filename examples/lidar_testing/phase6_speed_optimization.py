#!/usr/bin/env python3
"""
Phase 6: Speed Optimization

Tests square pattern navigation at increasing speeds to find optimal performance.

Optimization Strategy:
1. Start by centering robot (measure all 4 walls)
2. Remove artificial delays between movements
3. Only align if alignment error > threshold (skip if already aligned)
4. Test at increasing speeds: 8, 12, 16, 20, 24 cm/s
5. After each test, return to center for next iteration
6. Measure for each speed:
   - Total time to complete square
   - Position error at 4 control points (corners)
   - Max alignment error during run
   - Number of alignment corrections needed
   - Minimum wall distance (collision detection)

Goal: Find maximum speed where error is still acceptable.

=============================================================================
FINDINGS: Velocity Control Limitation
=============================================================================

Test Results:
- 8 cm/s:  ✓ Stable, no collisions, ~1cm stopping error
- 12 cm/s: ✓ Mostly stable, ~2cm stopping error (marginal)
- 16 cm/s: ✗ Collisions detected (min distance <13cm)
- 20 cm/s: ✗ Severe collisions
- 24 cm/s: ✗ Not tested due to safety concerns

Root Cause (discovered in Phase 6b):
  Velocity control + lidar feedback has FUNDAMENTAL limitation:
    Error ≈ Speed × (2 × Update_Period)

  At 10Hz update rate:
    - Control loop latency (~100ms) + motor deceleration
    - Error grows linearly with speed
    - Acceleration tuning has minimal effect

Collision Prevention:
  - Track minimum wall distance during each movement
  - Flag collision if min_distance < COLLISION_THRESHOLD (13cm)
  - Stop distance increased to 17cm for safety margin

Recommendations:
  1. For velocity control: Limit speed to ≤12 cm/s (safe, ~2cm error)
  2. For higher speeds (>12 cm/s):
     - Implement position control using Servo42D trajectory planning
     - Use predictive compensation: stop early based on speed
     - Increase control frequency to 50Hz (5× improvement)

See phase6b_stopping_accuracy.py for detailed analysis and measurements.

Usage:
    robot run examples/lidar_testing/phase6_speed_optimization.py

Test Procedure:
1. Place robot in center of arena, facing forward
2. Robot will test multiple speeds automatically
3. After each run, record metrics
4. Find optimal speed/accuracy tradeoff

Configuration:
- Test speeds: 0.08, 0.12, 0.16, 0.20, 0.24 m/s
- Alignment threshold: 3.0° (only align if error > 3°)
- Stop distance: 17cm from next wall (increased for safety)
- Target distance: 17cm from current wall (matches stop distance)
- Collision threshold: 13cm (flag if robot gets closer)
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1


def move_to_center(robot, arena_size=0.60):
    """
    Measure position from all 4 walls and move to center.

    Args:
        robot: Robot instance
        arena_size: Arena size in meters (default 0.60m = 60cm)
    """
    print("Measuring position from all walls...")

    # Measure distance to all 4 walls using check_wall (actual distance, not clearance)
    front_distance, _, _ = robot.lidar.check_wall(0)
    right_distance, _, _ = robot.lidar.check_wall(90)
    back_distance, _, _ = robot.lidar.check_wall(180)
    left_distance, _, _ = robot.lidar.check_wall(270)

    if front_distance:
        print(f"  Front (0°):   {front_distance*100:.1f}cm")
    if right_distance:
        print(f"  Right (90°):  {right_distance*100:.1f}cm")
    if back_distance:
        print(f"  Back (180°):  {back_distance*100:.1f}cm")
    if left_distance:
        print(f"  Left (270°):  {left_distance*100:.1f}cm")

    # Calculate center position (should be arena_size/2 from each wall)
    target_distance = arena_size / 2

    # Calculate required movement
    # Positive vx = move forward (toward 0°), negative = backward (toward 180°)
    # Positive vy = move left (toward 270°), negative = right (toward 90°)

    move_x = 0.0
    move_y = 0.0

    if front_distance and back_distance:
        # Calculate x-axis position error
        # If front_distance < target: need to move backward (negative vx)
        # If front_distance > target: need to move forward (positive vx)
        move_x = front_distance - target_distance

    if left_distance and right_distance:
        # Calculate y-axis position error
        # If left_distance < target: need to move right (negative vy)
        # If left_distance > target: need to move left (positive vy)
        move_y = left_distance - target_distance

    print(f"Moving to center: x={move_x*100:.1f}cm, y={move_y*100:.1f}cm")

    if abs(move_x) > 0.02 or abs(move_y) > 0.02:  # Only move if error > 2cm
        # Calculate movement time (at 8cm/s)
        distance = (move_x**2 + move_y**2) ** 0.5
        move_time = distance / 0.08

        # Normalize velocities to 8cm/s total speed
        if distance > 0:
            vx = (move_x / distance) * 0.08
            vy = (move_y / distance) * 0.08
        else:
            vx = vy = 0

        robot.drive.move(vx=vx, vy=vy)
        time.sleep(move_time)
        robot.drive.halt()
        print("  ✓ Moved to center")
    else:
        print("  ✓ Already at center")


def check_and_align_if_needed(robot, wall_angle, threshold=3.0, max_iterations=50):
    """
    Check alignment and only align if error exceeds threshold.

    Returns:
        tuple: (aligned_needed: bool, final_angle_error: float)
    """
    ROTATION_GAIN = 0.02
    MAX_ROTATION_SPEED = 0.3
    UPDATE_RATE = 5

    # Check current alignment
    distance, angle_deg, quality = robot.lidar.check_wall(wall_angle)

    if angle_deg is None:
        print(f"  ✗ No wall detected at {wall_angle}°")
        return False, None

    print(f"  Checking alignment to wall {wall_angle}°: {angle_deg:+.2f}°", end="")

    if abs(angle_deg) < threshold:
        print(f" - already aligned, skipping!")
        return False, angle_deg

    print(f" - needs alignment...")

    # Align
    for _ in range(max_iterations):
        distance, angle_deg, quality = robot.lidar.check_wall(wall_angle)

        if angle_deg is not None and abs(angle_deg) < 2.0:  # Align to 2° precision
            robot.drive.halt()
            print(f"  ✓ Aligned! angle: {angle_deg:+.2f}°, quality: {quality:.2f}")
            return True, angle_deg

        if angle_deg is not None:
            rotation_speed = ROTATION_GAIN * angle_deg
            rotation_speed = max(
                -MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, rotation_speed)
            )
            robot.drive.move(vtheta=rotation_speed)

        time.sleep(1.0 / UPDATE_RATE)

    robot.drive.halt()
    print(f"  ✗ Could not align to wall {wall_angle}°")
    return True, angle_deg


def move_to_wall(
    robot,
    vx,
    vy,
    target_wall_angle,
    follow_wall_angle=None,
    stop_distance=0.15,
    target_distance=0.14,
    max_time=15.0,
):
    """
    Move in direction (vx, vy) until target_wall is reached.
    Optionally maintain alignment and distance to follow_wall during movement.

    Returns:
        tuple: (success: bool, max_angle_error: float, actual_stop_distance: float, min_wall_distance: float)
    """
    ROTATION_GAIN = 0.02
    DISTANCE_GAIN = 0.3
    MAX_ROTATION_SPEED = 0.3
    UPDATE_RATE = 5

    start_time = time.time()
    max_angle_error = 0.0
    min_wall_distance = float("inf")  # Track minimum distance to any wall

    while time.time() - start_time < max_time:
        # Measure distance to all walls to detect collisions
        for wall_angle in [0, 90, 180, 270]:
            distance, _, _ = robot.lidar.check_wall(wall_angle)
            if distance is not None:
                min_wall_distance = min(min_wall_distance, distance)
        # Check target wall clearance
        target_clearance = robot.lidar.get_clearance(
            target_wall_angle, robot_width=0.22, angular_range=30.0
        )

        # Stop if reached target wall
        if target_clearance is not None and target_clearance <= stop_distance:
            robot.drive.halt()
            elapsed = time.time() - start_time
            return True, max_angle_error, target_clearance, min_wall_distance

        # Base movement
        move_vx = vx
        move_vy = vy
        move_vtheta = 0.0

        # If following a wall, maintain alignment and distance
        if follow_wall_angle is not None:
            distance, angle_deg, quality = robot.lidar.check_wall(follow_wall_angle)

            if distance is not None and angle_deg is not None:
                # Track max angle error
                max_angle_error = max(max_angle_error, abs(angle_deg))

                # Distance correction
                distance_error = distance - target_distance
                correction_factor = 1.0 + DISTANCE_GAIN * distance_error / abs(
                    vx if vx != 0 else vy
                )
                correction_factor = max(0.5, min(1.5, correction_factor))

                move_vx = vx * correction_factor
                move_vy = vy * correction_factor

                # Alignment correction
                move_vtheta = ROTATION_GAIN * angle_deg
                move_vtheta = max(
                    -MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, move_vtheta)
                )

        robot.drive.move(vx=move_vx, vy=move_vy, vtheta=move_vtheta)
        time.sleep(1.0 / UPDATE_RATE)

    robot.drive.halt()
    return False, max_angle_error, None, min_wall_distance


def run_square_pattern(robot, speed, alignment_threshold=3.0):
    """
    Run one complete square pattern at given speed.

    Returns:
        dict: Performance metrics (or None if collision detected)
    """
    STOP_DISTANCE = 0.17  # Stop at 17cm from next wall (more margin for higher speeds)
    TARGET_DISTANCE = 0.17  # Maintain 17cm from current wall while following
    COLLISION_THRESHOLD = (
        0.13  # 13cm - if robot gets closer than this, it's a collision
    )

    print()
    print("=" * 70)
    print(f"TESTING SPEED: {speed*100:.0f} cm/s")
    print("=" * 70)

    start_time = time.time()
    alignment_count = 0
    max_angle_errors = []
    position_errors = []  # Track position error at each control point
    min_wall_distances = []  # Track minimum wall distance for each segment
    collision_detected = False

    try:
        # Step 1: Forward to front wall (Control Point 1)
        print("\n  1. Forward → Front Wall (0°)")
        success, max_err, stop_dist, min_dist = move_to_wall(
            robot, vx=speed, vy=0, target_wall_angle=0, stop_distance=STOP_DISTANCE
        )
        if not success:
            return None
        max_angle_errors.append(max_err)
        min_wall_distances.append(min_dist)
        if min_dist < COLLISION_THRESHOLD:
            print(f"  ⚠ COLLISION! Min distance: {min_dist*100:.1f}cm")
            collision_detected = True
        if stop_dist:
            pos_err = abs(stop_dist - STOP_DISTANCE)
            position_errors.append(pos_err)
            print(
                f"  Stop: {stop_dist*100:.1f}cm (error: {pos_err*100:.1f}cm, min: {min_dist*100:.1f}cm)"
            )

        aligned, angle = check_and_align_if_needed(robot, 0, alignment_threshold)
        if aligned:
            alignment_count += 1

        # Step 2: Left (following front wall) to left wall (Control Point 2)
        print("\n  2. Left (following front) → Left Wall (270°)")
        success, max_err, stop_dist, min_dist = move_to_wall(
            robot,
            vx=0,
            vy=speed,
            target_wall_angle=270,
            follow_wall_angle=0,
            stop_distance=STOP_DISTANCE,
            target_distance=TARGET_DISTANCE,
        )
        if not success:
            return None
        max_angle_errors.append(max_err)
        min_wall_distances.append(min_dist)
        if min_dist < COLLISION_THRESHOLD:
            print(f"  ⚠ COLLISION! Min distance: {min_dist*100:.1f}cm")
            collision_detected = True
        if stop_dist:
            pos_err = abs(stop_dist - STOP_DISTANCE)
            position_errors.append(pos_err)
            print(
                f"  Stop: {stop_dist*100:.1f}cm (error: {pos_err*100:.1f}cm, min: {min_dist*100:.1f}cm)"
            )

        aligned, angle = check_and_align_if_needed(robot, 270, alignment_threshold)
        if aligned:
            alignment_count += 1

        # Step 3: Backward (following left wall) to back wall (Control Point 3)
        print("\n  3. Backward (following left) → Back Wall (180°)")
        success, max_err, stop_dist, min_dist = move_to_wall(
            robot,
            vx=-speed,
            vy=0,
            target_wall_angle=180,
            follow_wall_angle=270,
            stop_distance=STOP_DISTANCE,
            target_distance=TARGET_DISTANCE,
        )
        if not success:
            return None
        max_angle_errors.append(max_err)
        min_wall_distances.append(min_dist)
        if min_dist < COLLISION_THRESHOLD:
            print(f"  ⚠ COLLISION! Min distance: {min_dist*100:.1f}cm")
            collision_detected = True
        if stop_dist:
            pos_err = abs(stop_dist - STOP_DISTANCE)
            position_errors.append(pos_err)
            print(
                f"  Stop: {stop_dist*100:.1f}cm (error: {pos_err*100:.1f}cm, min: {min_dist*100:.1f}cm)"
            )

        aligned, angle = check_and_align_if_needed(robot, 180, alignment_threshold)
        if aligned:
            alignment_count += 1

        # Step 4: Right (following back wall) to right wall (Control Point 4)
        print("\n  4. Right (following back) → Right Wall (90°)")
        success, max_err, stop_dist, min_dist = move_to_wall(
            robot,
            vx=0,
            vy=-speed,
            target_wall_angle=90,
            follow_wall_angle=180,
            stop_distance=STOP_DISTANCE,
            target_distance=TARGET_DISTANCE,
        )
        if not success:
            return None
        max_angle_errors.append(max_err)
        min_wall_distances.append(min_dist)
        if min_dist < COLLISION_THRESHOLD:
            print(f"  ⚠ COLLISION! Min distance: {min_dist*100:.1f}cm")
            collision_detected = True
        if stop_dist:
            pos_err = abs(stop_dist - STOP_DISTANCE)
            position_errors.append(pos_err)
            print(
                f"  Stop: {stop_dist*100:.1f}cm (error: {pos_err*100:.1f}cm, min: {min_dist*100:.1f}cm)"
            )

        aligned, angle = check_and_align_if_needed(robot, 90, alignment_threshold)
        if aligned:
            alignment_count += 1

        # Step 5: Forward (following right wall) to front wall - final
        print("\n  5. Forward (following right) → Front Wall (0°)")
        success, max_err, stop_dist, min_dist = move_to_wall(
            robot,
            vx=speed,
            vy=0,
            target_wall_angle=0,
            follow_wall_angle=90,
            stop_distance=STOP_DISTANCE,
            target_distance=TARGET_DISTANCE,
        )
        if not success:
            return None
        max_angle_errors.append(max_err)
        min_wall_distances.append(min_dist)
        if min_dist < COLLISION_THRESHOLD:
            print(f"  ⚠ COLLISION! Min distance: {min_dist*100:.1f}cm")
            collision_detected = True

        total_time = time.time() - start_time

        # Calculate average and max position errors
        avg_pos_error = (
            sum(position_errors) / len(position_errors) if position_errors else 0
        )
        max_pos_error = max(position_errors) if position_errors else 0
        min_overall_distance = (
            min(min_wall_distances) if min_wall_distances else float("inf")
        )

        print()
        print("─" * 70)
        print(f"  Total time:        {total_time:.2f}s")
        print(f"  Alignments needed: {alignment_count}/5")
        print(
            f"  Max angle error:   {max(max_angle_errors) if max_angle_errors else 0:.2f}°"
        )
        print(f"  Avg position error: {avg_pos_error*100:.1f}cm")
        print(f"  Max position error: {max_pos_error*100:.1f}cm")
        print(f"  Min wall distance:  {min_overall_distance*100:.1f}cm")

        if collision_detected:
            print()
            print("  ⚠⚠⚠ COLLISION DETECTED - SPEED TOO HIGH ⚠⚠⚠")
            print("  Robot cannot safely stop at this speed")
            print("  Aligning and returning to center...")
            print("─" * 70)

            # Align to nearest wall
            robot.drive.halt()
            time.sleep(0.5)
            # Try to align to front wall (likely closest after collision)
            check_and_align_if_needed(robot, 0, alignment_threshold=2.0)
            time.sleep(0.5)

            # Move to center
            move_to_center(robot)

            # Return None to indicate test failed
            return None

        print("─" * 70)

        metrics = {
            "speed": speed,
            "total_time": total_time,
            "alignment_count": alignment_count,
            "max_angle_error": max(max_angle_errors) if max_angle_errors else 0,
            "avg_position_error": avg_pos_error,
            "max_position_error": max_pos_error,
            "min_wall_distance": min_overall_distance,
            "collision": False,
        }

        return metrics

    except Exception as e:
        print(f"  ✗ Error during run: {e}")
        return None


def main():
    print("=" * 70)
    print("Phase 6: Speed Optimization")
    print("=" * 70)
    print()
    print("This test finds optimal speed for square pattern navigation")
    print()
    print("Strategy:")
    print("  - Remove delays between movements")
    print("  - Only align if error > 3° threshold")
    print("  - Test increasing speeds: 8, 12, 16, 20, 24 cm/s")
    print("  - Measure time, errors, alignment count for each speed")
    print()
    print("Setup:")
    print("  1. Place robot in CENTER of arena")
    print("  2. Face robot FORWARD")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Test speeds (m/s)
    TEST_SPEEDS = [0.08, 0.12, 0.16, 0.20, 0.24]
    ALIGNMENT_THRESHOLD = 3.0  # Only align if error > 3°

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern="X", acceleration=50)
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    # Move to center before starting tests
    print()
    print("=" * 70)
    print("INITIAL CENTERING")
    print("=" * 70)
    print()
    move_to_center(robot)
    time.sleep(2)

    all_results = []

    try:
        for i, speed in enumerate(TEST_SPEEDS):
            metrics = run_square_pattern(robot, speed, ALIGNMENT_THRESHOLD)
            if metrics:
                all_results.append(metrics)

            # Move back to center for next iteration
            if i < len(TEST_SPEEDS) - 1:
                print()
                print("=" * 70)
                print("RETURNING TO CENTER FOR NEXT TEST")
                print("=" * 70)
                print()
                move_to_center(robot)
                time.sleep(2)

        # Summary
        print()
        print()
        print("=" * 70)
        print("OPTIMIZATION RESULTS")
        print("=" * 70)
        print()
        print(
            f"{'Speed':>8} │ {'Time':>7} │ {'Align':>6} │ {'Ang Err':>8} │ {'Pos Err':>8} │ {'Min Wall':>8} │ {'Speedup':>8}"
        )
        print("─" * 80)

        baseline_time = all_results[0]["total_time"] if all_results else 0

        for m in all_results:
            speed_str = f"{m['speed']*100:.0f} cm/s"
            time_str = f"{m['total_time']:.2f}s"
            align_str = f"{m['alignment_count']}/5"
            ang_err_str = f"{m['max_angle_error']:.2f}°"
            pos_err_str = f"{m['avg_position_error']*100:.1f}cm"
            min_wall_str = f"{m['min_wall_distance']*100:.1f}cm"
            speedup = baseline_time / m["total_time"] if m["total_time"] > 0 else 0
            speedup_str = f"{speedup:.2f}x"
            print(
                f"{speed_str:>8} │ {time_str:>7} │ {align_str:>6} │ {ang_err_str:>8} │ {pos_err_str:>8} │ {min_wall_str:>8} │ {speedup_str:>8}"
            )

        print()
        print("Recommendations:")
        print("  - Speed vs time tradeoff visible above")
        print("  - Lower alignment count = more efficient (less wasted time)")
        print("  - Angle error should stay < 5° for good control")
        print("  - Position error should stay < 3cm for accuracy")
        print("  - Min wall distance MUST stay > 12cm (collision threshold)")
        print("  - Choose fastest speed that meets all criteria")

    except KeyboardInterrupt:
        print()
        print("Testing interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 6 Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
