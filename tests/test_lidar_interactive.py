#!/usr/bin/env python3
"""
Interactive lidar testing tool for get_clearance() and check_wall().

Usage:
    robot run tests/test_lidar_interactive.py -- --angle 90 --robot-size 0.20
    robot run tests/test_lidar_interactive.py -- --angle 0 --robot-size 0.25 --max-range 1.0

Tests both functions continuously and displays results in real-time.
"""

import argparse
import time
from evabot import Robot, RPLidarC1


def format_angle_name(angle):
    """Get human-readable name for common angles."""
    angle_names = {
        0: "Front",
        90: "Right",
        180: "Back",
        270: "Left",
    }
    return angle_names.get(angle % 360, f"{angle}°")


def main():
    parser = argparse.ArgumentParser(description="Interactive lidar testing tool")
    parser.add_argument(
        "--angle",
        type=float,
        default=90,
        help="Angle to check in degrees (0=front, 90=right, 180=back, 270=left)",
    )
    parser.add_argument(
        "--robot-size",
        type=float,
        default=0.20,
        help="Robot width in meters (default: 0.20m = 20cm)",
    )
    parser.add_argument(
        "--max-range",
        type=float,
        default=None,
        help="Maximum lidar range in meters (default: None = unlimited)",
    )
    parser.add_argument(
        "--rate", type=float, default=10, help="Update rate in Hz (default: 10)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Interactive Lidar Testing Tool")
    print("=" * 70)
    print(f"Testing angle: {args.angle}° ({format_angle_name(args.angle)})")
    print(f"Robot size:    {args.robot_size}m ({args.robot_size*100:.1f}cm)")
    if args.max_range:
        print(f"Max range:     {args.max_range}m ({args.max_range*100:.0f}cm)")
    else:
        print(f"Max range:     Unlimited")
    print(f"Update rate:   {args.rate} Hz")
    print()
    print("Press Ctrl-C to stop")
    print("=" * 70)
    print()

    # Create robot with lidar
    robot = Robot()
    robot.lidar = RPLidarC1(max_range=args.max_range)
    robot.start()

    print("Waiting for lidar to initialize...")
    time.sleep(3)

    # Print header
    print()
    print("─" * 70)
    print(
        f"{'Time':>6} │ {'Clearance':>12} │ {'Distance':>10} │ {'Angle':>8} │ {'Quality':>7}"
    )
    print("─" * 70)

    try:
        start_time = time.time()
        loop_count = 0

        while True:
            elapsed = time.time() - start_time

            # Get clearance
            clearance = robot.lidar.get_clearance(
                args.angle, robot_width=args.robot_size
            )

            # Get wall info
            distance, angle_deg, quality = robot.lidar.check_wall(
                args.angle, max_residual=0.01, min_points=5, sample_range=10
            )

            # Format output
            time_str = f"{elapsed:.1f}s"

            if clearance is not None:
                clearance_str = f"{clearance:.3f}m ({clearance*100:.1f}cm)"
            else:
                clearance_str = "No data"

            if distance is not None:
                distance_str = f"{distance:.3f}m ({distance*100:.1f}cm)"
                angle_str = f"{angle_deg:+.2f}°"
                quality_str = f"{quality:.2f}"
            else:
                distance_str = "No wall"
                angle_str = "---"
                quality_str = "---"

            # Print line
            print(
                f"{time_str:>6} │ {clearance_str:>21} │ {distance_str:>17} │ {angle_str:>8} │ {quality_str:>7}",
                end="\r",
            )

            # Occasionally print on new line to keep history
            loop_count += 1
            if loop_count % 10 == 0:
                print()  # New line every 10 iterations

            time.sleep(1.0 / args.rate)

    except KeyboardInterrupt:
        print("\n")
        print("─" * 70)
        print("\nStopping...")

    robot.stop()

    print()
    print("=" * 70)
    print("Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
