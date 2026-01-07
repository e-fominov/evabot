#!/usr/bin/env python3
"""
Simple lidar test - just check if we can get data and test new functions.
"""

from evabot import Robot, RPLidarC1
import time


def main():
    print("=" * 60)
    print("Simple Lidar Test")
    print("=" * 60)

    # Create robot with just lidar
    robot = Robot()
    robot.lidar = RPLidarC1()
    robot.start()

    print("\nWaiting 5 seconds for lidar to initialize...")
    time.sleep(5)

    print("\nChecking raw scan data...")
    scan = robot.lidar.scan
    print(f"  Number of scan points: {len(scan)}")

    if len(scan) > 0:
        # Show some sample points
        angles = sorted(scan.keys())[:10]
        print(f"  First 10 angles: {angles}")
        for angle in angles:
            print(f"    {angle}°: {scan[angle]:.3f}m")

    print("\n" + "=" * 60)
    print("Testing Cardinal Directions")
    print("=" * 60)

    for _ in range(3):  # Try 3 times
        print("\nAttempt:")
        front = robot.lidar.front
        right = robot.lidar.right
        back = robot.lidar.back
        left = robot.lidar.left

        print(f"  Front (0°):   {front:.3f}m" if front else "  Front (0°):   No data")
        print(f"  Right (90°):  {right:.3f}m" if right else "  Right (90°):  No data")
        print(f"  Back (180°):  {back:.3f}m" if back else "  Back (180°):  No data")
        print(f"  Left (270°):  {left:.3f}m" if left else "  Left (270°):  No data")

        time.sleep(1)

    print("\n" + "=" * 60)
    print("Testing get_clearance()")
    print("=" * 60)

    for angle, name in [(0, "Front"), (90, "Right"), (180, "Back"), (270, "Left")]:
        clearance = robot.lidar.get_clearance(angle)
        if clearance:
            print(f"  {name:8s} ({angle:3d}°): {clearance:.3f}m ({clearance*100:.1f}cm)")
        else:
            print(f"  {name:8s} ({angle:3d}°): No data")

    print("\n" + "=" * 60)
    print("Testing check_wall() - PCA Line Fitting")
    print("=" * 60)

    for angle, name in [(0, "Front"), (90, "Right"), (180, "Back"), (270, "Left")]:
        distance, angle_deg, quality = robot.lidar.check_wall(angle)
        if distance is not None:
            print(f"  {name:8s} ({angle:3d}°): Wall at {distance:.3f}m ({distance*100:.1f}cm)")
            print(f"                     Angle error: {angle_deg:+.2f}° | Quality: {quality:.2f}")
        else:
            print(f"  {name:8s} ({angle:3d}°): No wall (corner/edge/parallel)")

    print("\n" + "=" * 60)
    print("Continuous monitoring for 10 seconds...")
    print("=" * 60)

    start_time = time.time()
    while time.time() - start_time < 10:
        front_clear = robot.lidar.get_clearance(0)
        distance, angle_deg, quality = robot.lidar.check_wall(0)

        status = "Front: "
        if front_clear:
            status += f"{front_clear*100:.1f}cm clear"
        else:
            status += "No data"

        if distance is not None:
            status += f" | Wall: {distance*100:.1f}cm, {angle_deg:+.1f}°, Q:{quality:.2f}"
        else:
            status += " | No wall"

        print(status, end='\r')
        time.sleep(0.1)

    print("\n\nStopping...")
    robot.stop()
    print("Done!")


if __name__ == "__main__":
    main()
