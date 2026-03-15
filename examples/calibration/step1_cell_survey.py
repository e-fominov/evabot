#!/usr/bin/env python3
"""
Step 1: Cell Survey - Map the maze cell walls with lidar.

Robot sits still inside a 30x30 cm cell (one wall open).
Reads all 4 directions to understand:
  - Which walls exist (3 closed + 1 open)
  - Distance to each wall
  - Angular alignment to each wall
  - Total cell dimensions (should be ~30cm)

This verifies the lidar is working correctly before any movement.

Usage:
    robot run examples/calibration/step1_cell_survey.py
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1

# Robot dimensions
ROBOT_WIDTH = 0.17  # 17cm square robot
CELL_SIZE = 0.30    # 30cm maze cell

# Expected wall distance if centered: (30 - 17) / 2 = 6.5 cm
EXPECTED_CENTERED = (CELL_SIZE - ROBOT_WIDTH) / 2  # 0.065m


def survey_walls(robot, num_samples=5, delay=0.3):
    """Take multiple readings of all walls and average them."""
    directions = {
        'Front (0)':   0,
        'Right (90)':  90,
        'Back (180)':  180,
        'Left (270)':  270,
    }

    results = {}
    for name, angle in directions.items():
        distances = []
        angles = []
        qualities = []

        for _ in range(num_samples):
            dist, ang, qual = robot.lidar.check_wall(angle)
            if dist is not None:
                distances.append(dist)
                angles.append(ang)
                qualities.append(qual)
            time.sleep(delay)

        if distances:
            results[name] = {
                'angle': angle,
                'distance': sum(distances) / len(distances),
                'angle_error': sum(angles) / len(angles),
                'quality': sum(qualities) / len(qualities),
                'samples': len(distances),
                'spread': max(distances) - min(distances) if len(distances) > 1 else 0,
            }
        else:
            results[name] = None

    return results


def main():
    print("=" * 60)
    print("Step 1: Cell Survey")
    print("=" * 60)
    print()
    print(f"Robot:  {ROBOT_WIDTH*100:.0f} x {ROBOT_WIDTH*100:.0f} cm")
    print(f"Cell:   {CELL_SIZE*100:.0f} x {CELL_SIZE*100:.0f} cm")
    print(f"Expected distance if centered: {EXPECTED_CENTERED*100:.1f} cm")
    print()

    # Initialize robot (no drive needed for this test)
    robot = Robot()
    # Still need drive for Robot to work, but we won't move
    robot.drive = MecanumDrive(
        fl=3, fr=4, bl=1, br=2,
        wheel_radius=0.03,  # 60mm wheels
        pattern="X",
    )
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print("Waiting for lidar to stabilize...")
    time.sleep(3)
    print()

    try:
        # === Survey 1: Quick scan ===
        print("-" * 60)
        print("Quick scan (single readings)")
        print("-" * 60)
        for name, angle in [('Front', 0), ('Right', 90), ('Back', 180), ('Left', 270)]:
            dist = getattr(robot.lidar, name.lower())
            print(f"  {name:6s}: {dist*100:.1f} cm" if dist else f"  {name:6s}: no reading")
        print()

        # === Survey 2: RANSAC wall detection ===
        print("-" * 60)
        print("RANSAC wall detection (5 samples each)")
        print("-" * 60)
        results = survey_walls(robot)

        open_wall = None
        wall_count = 0

        for name, data in results.items():
            if data is None:
                print(f"  {name:14s}: NO WALL (opening?)")
                open_wall = name
            else:
                wall_count += 1
                print(
                    f"  {name:14s}: "
                    f"dist={data['distance']*100:5.1f} cm  "
                    f"angle={data['angle_error']:+5.1f} deg  "
                    f"quality={data['quality']:.2f}  "
                    f"spread={data['spread']*100:.1f} cm  "
                    f"({data['samples']}/5 samples)"
                )
        print()

        # === Analysis ===
        print("-" * 60)
        print("Analysis")
        print("-" * 60)

        print(f"  Walls detected: {wall_count}/4")
        if open_wall:
            print(f"  Open wall:      {open_wall}")
        print()

        # Check opposite wall pairs for cell size
        pairs = [
            ('Front (0)', 'Back (180)', 'Front-Back'),
            ('Right (90)', 'Left (270)', 'Right-Left'),
        ]

        for name1, name2, pair_name in pairs:
            d1 = results.get(name1)
            d2 = results.get(name2)
            if d1 and d2:
                total = d1['distance'] + d2['distance'] + ROBOT_WIDTH
                error = total - CELL_SIZE
                print(
                    f"  {pair_name:12s} cell size: "
                    f"{d1['distance']*100:.1f} + {ROBOT_WIDTH*100:.0f} + {d2['distance']*100:.1f} "
                    f"= {total*100:.1f} cm (expected {CELL_SIZE*100:.0f} cm, error: {error*100:+.1f} cm)"
                )
            else:
                print(f"  {pair_name:12s} cell size: cannot measure (wall missing)")

        print()

        # Check alignment
        print("  Alignment:")
        for name, data in results.items():
            if data:
                status = "OK" if abs(data['angle_error']) < 2.0 else "MISALIGNED"
                print(f"    {name:14s}: {data['angle_error']:+5.1f} deg [{status}]")
        print()

        # Overall assessment
        print("-" * 60)
        print("Verdict")
        print("-" * 60)

        issues = []
        if wall_count < 3:
            issues.append(f"Only {wall_count} walls detected (expected 3)")

        for name, data in results.items():
            if data and abs(data['angle_error']) > 3.0:
                issues.append(f"{name} misaligned by {data['angle_error']:+.1f} deg")
            if data and data['spread'] > 0.01:
                issues.append(f"{name} readings inconsistent (spread {data['spread']*100:.1f} cm)")

        if not issues:
            print("  All checks passed! Ready for movement calibration.")
        else:
            print("  Issues found:")
            for issue in issues:
                print(f"    - {issue}")
            print()
            print("  Fix alignment before proceeding to movement calibration.")

    except KeyboardInterrupt:
        print("\nInterrupted")

    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()
    print()
    print("Done.")


if __name__ == "__main__":
    main()
