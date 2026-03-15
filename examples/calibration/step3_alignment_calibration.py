#!/usr/bin/env python3
"""
Step 3: Alignment Calibration - Auto-align to walls and verify precision.

Robot is in a 30x30 cm cell with left wall open (front/right/back closed).
Uses wall alignment to get perfectly parallel, then tests fine movements.

This is the "make sure everything is dialed in" script:
  1. Auto-align to front wall (get perfectly parallel)
  2. Verify alignment with all 3 walls
  3. Test 1cm forward, verify with lidar
  4. Test 1cm backward, verify with lidar
  5. Test 1cm right strafe, verify with lidar
  6. Test small rotation, verify alignment change

Usage:
    robot run examples/calibration/step3_alignment_calibration.py
"""

import time
import math
from evabot import Robot, MecanumDrive, RPLidarC1

WHEEL_RADIUS = 0.03  # 60mm wheels - adjust after step2 if needed
ROBOT_WIDTH = 0.17


def measure_wall(robot, angle, num_samples=5, delay=0.15):
    """Robust wall measurement with multiple samples."""
    distances = []
    angles = []
    qualities = []
    for _ in range(num_samples):
        d, a, q = robot.lidar.check_wall(angle)
        if d is not None:
            distances.append(d)
            angles.append(a)
            qualities.append(q)
        time.sleep(delay)

    if not distances:
        return None, None, None

    return (
        sum(distances) / len(distances),
        sum(angles) / len(angles),
        sum(qualities) / len(qualities),
    )


def auto_align(robot, wall_angle, tolerance_deg=0.5, max_iterations=20):
    """
    Auto-align robot parallel to a wall using proportional control.

    Rotates robot until angle_error from check_wall is within tolerance.
    """
    print(f"  Auto-aligning to wall at {wall_angle} degrees...")

    for i in range(max_iterations):
        dist, angle_error, quality = measure_wall(robot, wall_angle, num_samples=3)

        if dist is None:
            print(f"    Iteration {i+1}: no wall reading, skipping")
            continue

        print(f"    Iteration {i+1}: angle_error={angle_error:+.2f} deg, dist={dist*100:.1f} cm, q={quality:.2f}")

        if abs(angle_error) < tolerance_deg:
            print(f"  Aligned! (error {angle_error:+.2f} deg < {tolerance_deg} deg)")
            return True

        # Proportional rotation correction
        # angle_error positive = need to rotate CW (negative dtheta)
        correction_rad = math.radians(-angle_error * 0.7)  # 70% of error, conservative
        correction_rad = max(-math.radians(5), min(math.radians(5), correction_rad))  # limit to 5 deg

        robot.drive.zero_position()
        robot.drive.move_by(dtheta=correction_rad, speed=0.03, timeout=5.0)
        time.sleep(0.3)

    print(f"  Failed to align after {max_iterations} iterations")
    return False


def precision_move_test(robot, dx, dy, wall_angle, description):
    """Make a small move and verify with lidar."""
    # Measure before
    dist_before, ang_before, _ = measure_wall(robot, wall_angle)
    if dist_before is None:
        print(f"    {description}: SKIP (no wall reading)")
        return None

    # Move
    robot.drive.zero_position()
    robot.drive.move_by(dx=dx, dy=dy, speed=0.03, timeout=10.0)
    time.sleep(0.5)

    # Measure after
    dist_after, ang_after, _ = measure_wall(robot, wall_angle)
    if dist_after is None:
        print(f"    {description}: SKIP (no reading after move)")
        return None

    # Expected change in distance to wall
    # Moving toward wall = distance decreases
    actual_change = (dist_before - dist_after) * 100  # cm, positive = closer

    # What we expected
    if wall_angle == 0:
        expected_change = dx * 100      # forward = closer to front
    elif wall_angle == 180:
        expected_change = -dx * 100     # forward = farther from back
    elif wall_angle == 90:
        expected_change = -dy * 100     # strafe left = farther from right
    elif wall_angle == 270:
        expected_change = dy * 100      # strafe left = closer to left
    else:
        expected_change = 0

    error = actual_change - expected_change
    print(
        f"    {description}: "
        f"expected {expected_change:+.2f} cm, "
        f"actual {actual_change:+.2f} cm, "
        f"error {error:+.2f} cm, "
        f"alignment {ang_after:+.1f} deg"
    )

    return actual_change, expected_change, error


def main():
    print("=" * 60)
    print("Step 3: Alignment & Precision Calibration")
    print("=" * 60)
    print()
    print("Cell layout: left wall OPEN, front/right/back CLOSED")
    print(f"Wheel radius: {WHEEL_RADIUS*1000:.0f} mm")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    robot = Robot()
    robot.drive = MecanumDrive(
        fl=3, fr=4, bl=1, br=2,
        wheel_radius=WHEEL_RADIUS,
        pattern="X",
        acceleration=50,
    )
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print("Waiting for lidar...")
    time.sleep(3)

    try:
        # === Phase 1: Initial survey ===
        print()
        print("-" * 60)
        print("Phase 1: Initial wall readings")
        print("-" * 60)
        for name, angle in [('Front', 0), ('Right', 90), ('Back', 180), ('Left', 270)]:
            d, a, q = measure_wall(robot, angle)
            if d is not None:
                print(f"  {name:6s}: {d*100:5.1f} cm, angle={a:+.1f} deg, q={q:.2f}")
            else:
                print(f"  {name:6s}: no wall (opening)")

        # === Phase 2: Auto-align to front wall ===
        print()
        print("-" * 60)
        print("Phase 2: Auto-align to front wall")
        print("-" * 60)
        aligned = auto_align(robot, wall_angle=0, tolerance_deg=0.5)

        if not aligned:
            print("Cannot align - check robot position")
            return

        # Verify alignment with all walls
        print()
        print("  Verification after alignment:")
        for name, angle in [('Front', 0), ('Right', 90), ('Back', 180)]:
            d, a, q = measure_wall(robot, angle)
            if d is not None:
                status = "OK" if abs(a) < 1.0 else "off"
                print(f"    {name:6s}: {d*100:5.1f} cm, angle={a:+.1f} deg [{status}]")

        # === Phase 3: Precision movement tests ===
        print()
        print("-" * 60)
        print("Phase 3: Precision movement tests (1 cm each)")
        print("-" * 60)

        results = []

        # Test 1: Forward 1cm (check front wall)
        r = precision_move_test(robot, dx=0.01, dy=0, wall_angle=0, description="Forward 1cm")
        if r: results.append(('fwd', r))

        # Move back
        robot.drive.zero_position()
        robot.drive.move_by(dx=-0.01, speed=0.03, timeout=5.0)
        time.sleep(0.3)

        # Test 2: Backward 1cm (check back wall)
        r = precision_move_test(robot, dx=-0.01, dy=0, wall_angle=180, description="Backward 1cm")
        if r: results.append(('bwd', r))

        # Move back
        robot.drive.zero_position()
        robot.drive.move_by(dx=0.01, speed=0.03, timeout=5.0)
        time.sleep(0.3)

        # Test 3: Right strafe 1cm (check right wall)
        r = precision_move_test(robot, dx=0, dy=-0.01, wall_angle=90, description="Right 1cm")
        if r: results.append(('right', r))

        # Move back
        robot.drive.zero_position()
        robot.drive.move_by(dy=0.01, speed=0.03, timeout=5.0)
        time.sleep(0.3)

        # Test 4: Forward 2cm
        r = precision_move_test(robot, dx=0.02, dy=0, wall_angle=0, description="Forward 2cm")
        if r: results.append(('fwd2', r))

        # Move back
        robot.drive.zero_position()
        robot.drive.move_by(dx=-0.02, speed=0.03, timeout=5.0)
        time.sleep(0.3)

        # === Phase 4: Rotation test ===
        print()
        print("-" * 60)
        print("Phase 4: Rotation precision")
        print("-" * 60)

        for angle in [5, -5, 10, -10]:
            _, ang_before, _ = measure_wall(robot, 0)
            robot.drive.zero_position()
            robot.drive.move_by(dtheta=math.radians(angle), speed=0.03, timeout=5.0)
            time.sleep(0.5)
            _, ang_after, _ = measure_wall(robot, 0)

            if ang_before is not None and ang_after is not None:
                measured = ang_after - ang_before
                error = measured - angle
                print(f"    Rotate {angle:+3d} deg: measured change {measured:+.1f} deg, error {error:+.1f} deg")
            else:
                print(f"    Rotate {angle:+3d} deg: measurement failed")

            # Rotate back
            robot.drive.zero_position()
            robot.drive.move_by(dtheta=math.radians(-angle), speed=0.03, timeout=5.0)
            time.sleep(0.3)

        # === Summary ===
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)

        if results:
            errors = [abs(r[1][2]) for r in results]  # absolute errors in cm
            avg_error = sum(errors) / len(errors)
            max_error = max(errors)

            # Calculate scaling factor
            ratios = []
            for name, (actual, expected, err) in results:
                if expected != 0:
                    ratios.append(actual / expected)

            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                print(f"  Avg movement ratio: {avg_ratio:.3f} (1.000 = perfect)")
                print(f"  Avg position error: {avg_error:.2f} cm")
                print(f"  Max position error: {max_error:.2f} cm")

                if abs(avg_ratio - 1.0) < 0.05:
                    print(f"\n  wheel_radius = {WHEEL_RADIUS:.4f} is CORRECT")
                else:
                    new_radius = WHEEL_RADIUS * avg_ratio
                    print(f"\n  Suggested wheel_radius: {new_radius:.4f} ({new_radius*1000:.1f} mm)")

                if avg_error < 0.2:
                    print("  Precision: EXCELLENT (<2mm)")
                elif avg_error < 0.5:
                    print("  Precision: GOOD (<5mm)")
                else:
                    print("  Precision: NEEDS WORK")

        print()
        print("Robot is calibrated and ready for maze navigation!")

    except KeyboardInterrupt:
        print("\nInterrupted!")

    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()
    print("Done.")


if __name__ == "__main__":
    main()
