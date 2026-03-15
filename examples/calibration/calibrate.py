#!/usr/bin/env python3
"""
Practical calibration: move 2cm in each direction, verify with lidar.
"""

import time
import math
from evabot import Robot, MecanumDrive, RPLidarC1


def wall(robot, angle, n=3):
    """Quick wall measurement, averaged."""
    dists = []
    for _ in range(n):
        d, a, q = robot.lidar.check_wall(angle)
        if d is not None:
            dists.append(d)
        time.sleep(0.15)
    if not dists:
        return None
    return sum(dists) / len(dists)


def walls(robot):
    """Print all wall distances."""
    for name, angle in [("Front", 0), ("Right", 90), ("Back", 180), ("Left", 270)]:
        d = wall(robot, angle)
        if d and d < 0.40:
            print(f"  {name:6s}: {d*100:.1f} cm")
        else:
            print(f"  {name:6s}: {'open' if d and d > 0.40 else 'no reading'}")


def test_move(robot, label, dx=0, dy=0, dtheta=0, check_angle=0):
    """Move, measure wall before/after, report error."""
    before = wall(robot, check_angle)
    if before is None:
        print(f"  {label}: no wall reading before move")
        return

    robot.drive.zero_position()
    robot.drive.move_by(dx=dx, dy=dy, dtheta=dtheta, speed=0.05, timeout=10)
    time.sleep(0.5)

    after = wall(robot, check_angle)
    if after is None:
        print(f"  {label}: no wall reading after move")
        return

    change = (before - after) * 100  # positive = got closer
    expected = 0
    if check_angle == 0:
        expected = dx * 100
    elif check_angle == 180:
        expected = -dx * 100
    elif check_angle == 90:
        expected = -dy * 100
    elif check_angle == 270:
        expected = dy * 100

    error = change - expected
    print(
        f"  {label}: before={before*100:.1f}cm, after={after*100:.1f}cm, "
        f"moved={change:+.1f}cm (expected {expected:+.1f}cm, error={error:+.1f}cm)"
    )
    return change


def test_rotation(robot, label, angle_deg, check_angle=0):
    """Rotate, check wall angle before/after."""
    _, ang_before, _ = robot.lidar.check_wall(check_angle)
    if ang_before is None:
        print(f"  {label}: no reading before")
        return

    robot.drive.zero_position()
    robot.drive.move_by(dtheta=math.radians(angle_deg), speed=0.05, timeout=10)
    time.sleep(0.5)

    _, ang_after, _ = robot.lidar.check_wall(check_angle)
    if ang_after is None:
        print(f"  {label}: no reading after")
        return

    measured = ang_after - ang_before
    print(
        f"  {label}: wall angle before={ang_before:+.1f}, after={ang_after:+.1f}, "
        f"change={measured:+.1f} deg (expected {angle_deg:+.1f} deg)"
    )


def auto_align(robot, wall_angle=0, tolerance=1.0, max_iter=15):
    """Align parallel to wall."""
    for i in range(max_iter):
        d, angle_err, q = robot.lidar.check_wall(wall_angle)
        if d is None:
            print(f"    iter {i+1}: no reading")
            continue
        print(f"    iter {i+1}: dist={d*100:.1f}cm, angle={angle_err:+.1f} deg")
        if abs(angle_err) < tolerance:
            print(f"    Aligned!")
            return True
        correction = math.radians(angle_err * 0.8)
        # Minimum correction to overcome friction
        if abs(correction) < math.radians(2.0):
            correction = math.copysign(math.radians(2.0), correction)
        correction = max(-math.radians(10), min(math.radians(10), correction))
        robot.drive.zero_position()
        robot.drive.move_by(dtheta=correction, speed=0.03, timeout=5)
        time.sleep(0.3)
    return False


def approach_wall(robot, wall_angle, target_cm, speed=0.05):
    """Move toward wall and stop at target distance."""
    direction_map = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}
    vx_dir, vy_dir = direction_map[wall_angle]

    for i in range(30):
        d = wall(robot, wall_angle, n=2)
        if d is None:
            print(f"    lost wall reading, stopping")
            robot.drive.halt()
            return
        remaining = d * 100 - target_cm
        print(f"    dist={d*100:.1f}cm, remaining={remaining:.1f}cm")
        if remaining < 0.3:
            robot.drive.halt()
            print(f"    Reached target!")
            return
        # Move a fraction of remaining, with minimum to overcome friction
        step = min(remaining / 100, 0.02)  # max 2cm steps
        step = max(step, 0.005)  # min 5mm to overcome friction
        robot.drive.zero_position()
        robot.drive.move_by(dx=step * vx_dir, dy=step * vy_dir, speed=speed, timeout=5)
        time.sleep(0.3)
    robot.drive.halt()


def main():
    print("=" * 50)
    print("Calibration")
    print("=" * 50)
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    robot = Robot()
    robot.drive = MecanumDrive(
        fl=3,
        fr=4,
        bl=1,
        br=2,
        wheel_radius=0.016,
        wheel_base=0.040,   # tuned for rotation accuracy
        track_width=0.095,  # tuned for rotation accuracy
        pattern="X",
        acceleration=50,
    )
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()
    time.sleep(3)

    try:
        # --- Initial readings ---
        print()
        print("--- Initial wall readings ---")
        walls(robot)

        # --- Test 1: Forward 2cm ---
        print()
        print("--- Test 1: Forward 2cm (check front wall) ---")
        test_move(robot, "fwd 2cm", dx=0.02, check_angle=0)

        # Move back
        print("  (returning)")
        robot.drive.zero_position()
        robot.drive.move_by(dx=-0.02, speed=0.05, timeout=10)
        time.sleep(0.5)

        # --- Test 2: Backward 2cm ---
        print()
        print("--- Test 2: Backward 2cm (check back wall) ---")
        test_move(robot, "bwd 2cm", dx=-0.02, check_angle=180)

        # Move back
        print("  (returning)")
        robot.drive.zero_position()
        robot.drive.move_by(dx=0.02, speed=0.05, timeout=10)
        time.sleep(0.5)

        # --- Test 3: Right 2cm ---
        print()
        print("--- Test 3: Right strafe 2cm (check right wall) ---")
        test_move(robot, "right 2cm", dy=-0.02, check_angle=90)

        # Move back
        print("  (returning)")
        robot.drive.zero_position()
        robot.drive.move_by(dy=0.02, speed=0.05, timeout=10)
        time.sleep(0.5)

        # --- Test 4: Left 2cm (open wall - check that back wall stays same) ---
        print()
        print("--- Test 4: Left strafe 2cm (check back wall stays same) ---")
        test_move(robot, "left 2cm", dy=0.02, check_angle=180)

        # Move back
        print("  (returning)")
        robot.drive.zero_position()
        robot.drive.move_by(dy=-0.02, speed=0.05, timeout=10)
        time.sleep(0.5)

        # --- Test 5: Rotation ---
        print()
        print("--- Test 5: Rotation 10 degrees CW ---")
        test_rotation(robot, "rotate CW 10", angle_deg=-10, check_angle=0)

        # Rotate back
        print("  (returning)")
        robot.drive.zero_position()
        robot.drive.move_by(dtheta=math.radians(10), speed=0.05, timeout=10)
        time.sleep(0.5)

        print()
        print("--- Test 6: Rotation 10 degrees CCW ---")
        test_rotation(robot, "rotate CCW 10", angle_deg=10, check_angle=0)

        # Rotate back
        print("  (returning)")
        robot.drive.zero_position()
        robot.drive.move_by(dtheta=math.radians(-10), speed=0.05, timeout=10)
        time.sleep(0.5)

        # --- Test 7: Auto-align to front wall ---
        print()
        print("--- Test 7: Auto-align to front wall ---")
        auto_align(robot, wall_angle=0, tolerance=1.0)

        # --- Test 8: Approach front wall and stop at 10cm ---
        print()
        print("--- Test 8: Approach front wall, stop at 10cm ---")
        d = wall(robot, 0)
        if d and d * 100 > 12:
            approach_wall(robot, wall_angle=0, target_cm=10.0, speed=0.05)
        else:
            print("  Already too close, skipping")

        print()
        print("--- Final wall readings ---")
        walls(robot)

    except KeyboardInterrupt:
        print("\nInterrupted!")

    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()
    print("\nDone.")


if __name__ == "__main__":
    main()
