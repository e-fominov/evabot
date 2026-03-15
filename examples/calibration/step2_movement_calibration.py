#!/usr/bin/env python3
"""
Step 2: Movement Calibration - Verify small moves with lidar feedback.

Robot is in a 30x30 cm cell with 3 walls. Makes tiny moves (1-2 cm)
toward each wall and verifies the actual displacement via lidar.

Tests:
  1. Forward movement accuracy (toward front wall)
  2. Backward movement accuracy (toward back wall)
  3. Left strafe accuracy (toward left wall)
  4. Right strafe accuracy (toward right wall)
  5. Rotation accuracy (small angle, check with wall alignment)

If movements are consistently off by a factor, the wheel_radius
parameter needs adjustment. The script calculates the correction.

Usage:
    robot run examples/calibration/step2_movement_calibration.py
"""

import time
import math
from evabot import Robot, MecanumDrive, RPLidarC1

# Robot config
WHEEL_RADIUS = 0.03  # 60mm diameter wheels = 30mm radius
ROBOT_WIDTH = 0.17   # 17cm square
CELL_SIZE = 0.30     # 30cm cell


def measure_wall(robot, angle, num_samples=3, delay=0.2):
    """Average multiple wall readings for accuracy."""
    distances = []
    angles = []
    for _ in range(num_samples):
        d, a, q = robot.lidar.check_wall(angle)
        if d is not None and q is not None and q > 0.3:
            distances.append(d)
            if a is not None:
                angles.append(a)
        time.sleep(delay)

    if not distances:
        return None, None
    return sum(distances) / len(distances), (sum(angles) / len(angles) if angles else None)


def test_linear_move(robot, direction, wall_angle, move_cm, speed=0.05):
    """
    Test a linear move and verify with lidar.

    Args:
        direction: 'forward', 'backward', 'left', 'right'
        wall_angle: lidar angle to measure (wall we're moving toward)
        move_cm: distance to move in cm (positive = toward wall)
        speed: movement speed m/s

    Returns:
        (expected_cm, actual_cm, error_cm) or None if failed
    """
    move_m = move_cm / 100.0

    # Map direction to dx/dy
    move_map = {
        'forward':  (move_m, 0),
        'backward': (-move_m, 0),
        'left':     (0, move_m),
        'right':    (0, -move_m),
    }
    dx, dy = move_map[direction]

    # Measure before
    dist_before, _ = measure_wall(robot, wall_angle)
    if dist_before is None:
        print(f"    Cannot measure wall at {wall_angle} deg")
        return None

    # Execute move
    robot.drive.zero_position()
    robot.drive.move_by(dx=dx, dy=dy, speed=speed, timeout=10.0)
    time.sleep(0.5)  # settle

    # Measure after
    dist_after, _ = measure_wall(robot, wall_angle)
    if dist_after is None:
        print(f"    Cannot measure wall at {wall_angle} deg after move")
        return None

    # Calculate actual displacement (positive = closer to wall)
    actual_cm = (dist_before - dist_after) * 100.0
    error_cm = actual_cm - move_cm

    return move_cm, actual_cm, error_cm


def test_rotation(robot, angle_deg, wall_angle, speed=0.05):
    """
    Test a small rotation and verify with wall alignment.

    Args:
        angle_deg: rotation in degrees (positive = CCW)
        wall_angle: wall to check alignment against
        speed: movement speed

    Returns:
        (expected_deg, actual_deg, error_deg) or None
    """
    # Measure alignment before
    _, angle_before = measure_wall(robot, wall_angle)
    if angle_before is None:
        print(f"    Cannot measure wall alignment at {wall_angle} deg")
        return None

    # Execute rotation
    dtheta = math.radians(angle_deg)
    robot.drive.zero_position()
    robot.drive.move_by(dtheta=dtheta, speed=speed, timeout=10.0)
    time.sleep(0.5)  # settle

    # Measure alignment after
    _, angle_after = measure_wall(robot, wall_angle)
    if angle_after is None:
        print(f"    Cannot measure wall alignment after rotation")
        return None

    # Actual rotation = change in wall angle
    actual_deg = angle_after - angle_before
    error_deg = actual_deg - angle_deg

    return angle_deg, actual_deg, error_deg


def run_linear_tests(robot):
    """Run forward/backward/strafe tests."""
    print()
    print("=" * 60)
    print("LINEAR MOVEMENT TESTS")
    print("=" * 60)

    # Determine which walls exist
    walls = {}
    for name, angle in [('front', 0), ('right', 90), ('back', 180), ('left', 270)]:
        d, _ = measure_wall(robot, angle)
        if d is not None:
            walls[name] = (angle, d)
            print(f"  {name:6s} wall: {d*100:.1f} cm")
        else:
            print(f"  {name:6s} wall: not detected")
    print()

    # Test plan: move toward each detected wall, then move back
    tests = []

    if 'front' in walls and walls['front'][1] > 0.04:
        tests.append(('forward', 0, 'front'))
    if 'back' in walls and walls['back'][1] > 0.04:
        tests.append(('backward', 180, 'back'))
    if 'left' in walls and walls['left'][1] > 0.04:
        tests.append(('left', 270, 'left'))
    if 'right' in walls and walls['right'][1] > 0.04:
        tests.append(('right', 90, 'right'))

    if not tests:
        print("  No walls close enough to test against!")
        return []

    all_results = []

    for direction, wall_angle, wall_name in tests:
        print(f"-" * 60)
        print(f"Testing: {direction} (toward {wall_name} wall)")
        print(f"-" * 60)

        # Test with 1cm and 2cm moves
        for move_cm in [1.0, 2.0]:
            print(f"\n  Move {move_cm:.0f} cm {direction}:")
            result = test_linear_move(robot, direction, wall_angle, move_cm)

            if result:
                expected, actual, error = result
                ratio = actual / expected if expected != 0 else 0
                status = "OK" if abs(error) < 0.3 else "DRIFT" if abs(error) < 0.5 else "BAD"
                print(
                    f"    Expected: {expected:+5.1f} cm"
                    f"  Actual: {actual:+5.1f} cm"
                    f"  Error: {error:+5.2f} cm"
                    f"  Ratio: {ratio:.3f}"
                    f"  [{status}]"
                )
                all_results.append((direction, move_cm, expected, actual, error, ratio))
            else:
                print(f"    FAILED - could not measure")

            # Move back to roughly original position
            print(f"    Returning...")
            opp_map = {'forward': 'backward', 'backward': 'forward', 'left': 'right', 'right': 'left'}
            opp_dir = opp_map[direction]
            dx_back, dy_back = {
                'forward': (-move_cm/100, 0),
                'backward': (move_cm/100, 0),
                'left': (0, -move_cm/100),
                'right': (0, move_cm/100),
            }[direction]
            robot.drive.zero_position()
            robot.drive.move_by(dx=dx_back, dy=dy_back, speed=0.05, timeout=10.0)
            time.sleep(0.5)

    return all_results


def run_rotation_tests(robot):
    """Run small rotation tests."""
    print()
    print("=" * 60)
    print("ROTATION TESTS")
    print("=" * 60)

    # Find a wall to measure alignment against
    best_wall = None
    for name, angle in [('front', 0), ('right', 90), ('back', 180), ('left', 270)]:
        d, a = measure_wall(robot, angle)
        if d is not None and a is not None:
            best_wall = (name, angle)
            print(f"  Using {name} wall for alignment reference")
            break

    if not best_wall:
        print("  No wall available for rotation test!")
        return []

    wall_name, wall_angle = best_wall
    all_results = []

    for angle_deg in [5.0, -5.0, 10.0, -10.0]:
        print(f"\n  Rotate {angle_deg:+.0f} degrees:")
        result = test_rotation(robot, angle_deg, wall_angle)

        if result:
            expected, actual, error = result
            status = "OK" if abs(error) < 1.0 else "DRIFT" if abs(error) < 2.0 else "BAD"
            print(
                f"    Expected: {expected:+6.1f} deg"
                f"  Actual: {actual:+6.1f} deg"
                f"  Error: {error:+5.1f} deg"
                f"  [{status}]"
            )
            all_results.append((angle_deg, expected, actual, error))
        else:
            print(f"    FAILED")

        # Rotate back
        robot.drive.zero_position()
        robot.drive.move_by(dtheta=math.radians(-angle_deg), speed=0.05, timeout=10.0)
        time.sleep(0.5)

    return all_results


def main():
    print("=" * 60)
    print("Step 2: Movement Calibration")
    print("=" * 60)
    print()
    print(f"Wheel radius: {WHEEL_RADIUS*1000:.0f} mm (60mm wheels)")
    print(f"Robot size:   {ROBOT_WIDTH*100:.0f} x {ROBOT_WIDTH*100:.0f} cm")
    print(f"Cell size:    {CELL_SIZE*100:.0f} x {CELL_SIZE*100:.0f} cm")
    print()
    print("Will make tiny moves (1-2 cm) and verify with lidar.")
    print("Keep hands ready for e-stop (Ctrl+C)!")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(
        fl=3, fr=4, bl=1, br=2,
        wheel_radius=WHEEL_RADIUS,
        pattern="X",
        acceleration=50,  # smooth for calibration
    )
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print("Waiting for lidar to stabilize...")
    time.sleep(3)

    try:
        # Run linear tests
        linear_results = run_linear_tests(robot)

        # Run rotation tests
        rotation_results = run_rotation_tests(robot)

        # === Summary ===
        print()
        print("=" * 60)
        print("CALIBRATION SUMMARY")
        print("=" * 60)

        if linear_results:
            ratios = [r[5] for r in linear_results if r[5] > 0]
            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                corrected_radius = WHEEL_RADIUS * avg_ratio
                print()
                print(f"  Linear tests: {len(linear_results)} completed")
                print(f"  Average move ratio (actual/expected): {avg_ratio:.3f}")
                print()

                if abs(avg_ratio - 1.0) < 0.05:
                    print(f"  Wheel radius {WHEEL_RADIUS*1000:.1f} mm is CORRECT (within 5%)")
                else:
                    print(f"  Current wheel_radius:   {WHEEL_RADIUS*1000:.1f} mm")
                    print(f"  Suggested wheel_radius: {corrected_radius*1000:.1f} mm")
                    print()
                    print(f"  To fix, use:")
                    print(f"    MecanumDrive(..., wheel_radius={corrected_radius:.4f})")
        else:
            print("  No linear test results")

        if rotation_results:
            errors = [abs(r[3]) for r in rotation_results]
            avg_error = sum(errors) / len(errors)
            print()
            print(f"  Rotation tests: {len(rotation_results)} completed")
            print(f"  Average rotation error: {avg_error:.1f} degrees")

            if avg_error < 2.0:
                print(f"  Rotation accuracy is GOOD")
            else:
                print(f"  Rotation needs attention - check wheel_base/track_width")
        else:
            print("  No rotation test results")

        print()
        print("=" * 60)

    except KeyboardInterrupt:
        print("\nInterrupted!")

    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()
    print("Done.")


if __name__ == "__main__":
    main()
