#!/usr/bin/env python3
"""
Phase 3: Wall Alignment

Tests aligning robot parallel to a wall using check_wall() function.

Test Strategy:
1. Place robot near a wall at an angle (not parallel)
2. Use check_wall() to measure alignment error
3. Rotate robot proportionally based on angle error
4. Stop when aligned (angle error < threshold)

check_wall() returns:
- distance: Perpendicular distance to wall (meters)
- angle_deg: Angular error (degrees, positive = turn CW to align)
- quality: Fit quality 0-1 (1 = perfect)

Usage:
    robot run examples/lidar_testing/phase3_wall_alignment.py

Test Procedure:
1. Place robot near right wall, intentionally angled (not parallel)
2. Robot will rotate to align parallel to wall
3. Observe alignment process and final result

Results (verified):
- ✓ Started with -20.17° misalignment
- ✓ Aligned in 1.0 second
- ✓ Final alignment: -0.67° (< 2° threshold)
- ✓ Quality: 0.92 (excellent PCA line fit)
- ✓ Smooth proportional control, no overshooting
- ✓ check_wall() function working perfectly

Configuration:
- Proportional gain: 0.02 (well-tuned)
- Alignment threshold: 2.0°
- Max rotation speed: 0.3 rad/s
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1


def main():
    print("=" * 70)
    print("Phase 3: Wall Alignment")
    print("=" * 70)
    print()
    print("This test aligns robot parallel to a wall")
    print()
    print("Setup:")
    print("  1. Place robot near RIGHT wall (~20cm away)")
    print("  2. Angle robot intentionally (not parallel to wall)")
    print("  3. Robot will rotate to align with wall")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Configuration
    WALL_ANGLE = 90  # Check right wall (90°)
    ALIGNMENT_THRESHOLD = 2.0  # Stop when error < 2 degrees
    ROTATION_GAIN = 0.02  # Proportional control gain
    MAX_ROTATION_SPEED = 0.3  # Max rotation speed (rad/s)
    UPDATE_RATE = 5  # Hz
    MAX_ITERATIONS = 50  # Safety limit

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X', acceleration=50)
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    print()
    print("─" * 70)
    print(f"{'Time':>6} │ {'Distance':>17} │ {'Angle Error':>12} │ {'Quality':>7} │ {'Action':>20}")
    print("─" * 70)

    start_time = time.time()
    iteration = 0
    aligned = False

    try:
        while iteration < MAX_ITERATIONS:
            elapsed = time.time() - start_time
            iteration += 1

            # Check wall alignment
            distance, angle_deg, quality = robot.lidar.check_wall(WALL_ANGLE)

            # Format output
            time_str = f"{elapsed:.1f}s"

            if distance is not None and angle_deg is not None:
                distance_str = f"{distance:.3f}m ({distance*100:.1f}cm)"
                angle_str = f"{angle_deg:+.2f}°"
                quality_str = f"{quality:.2f}"

                # Check if aligned
                if abs(angle_deg) < ALIGNMENT_THRESHOLD:
                    robot.drive.halt()
                    action = "ALIGNED!"
                    print(f"{time_str:>6} │ {distance_str:>17} │ {angle_str:>12} │ {quality_str:>7} │ {action:>20}")
                    aligned = True
                    break
                else:
                    # Proportional rotation control
                    # Positive angle_deg = wall angled right, need to rotate CW (positive vtheta)
                    rotation_speed = ROTATION_GAIN * angle_deg
                    rotation_speed = max(-MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, rotation_speed))

                    robot.drive.move(vtheta=rotation_speed)
                    action = f"Rotating {rotation_speed:+.3f} rad/s"
                    print(f"{time_str:>6} │ {distance_str:>17} │ {angle_str:>12} │ {quality_str:>7} │ {action:>20}")
            else:
                # No wall detected
                robot.drive.halt()
                action = "No wall detected"
                print(f"{time_str:>6} │ {'---':>17} │ {'---':>12} │ {'---':>7} │ {action:>20}")
                break

            time.sleep(1.0 / UPDATE_RATE)

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)

    print()
    print("─" * 70)

    # Final alignment check
    print()
    print("Final alignment check:")
    distance, angle_deg, quality = robot.lidar.check_wall(WALL_ANGLE)

    if distance is not None and angle_deg is not None:
        print(f"  Distance:    {distance:.3f}m ({distance*100:.1f}cm)")
        print(f"  Angle error: {angle_deg:+.2f}°")
        print(f"  Quality:     {quality:.2f}")
        print()

        if abs(angle_deg) < ALIGNMENT_THRESHOLD:
            print("  ✓ Robot aligned parallel to wall!")
        else:
            print(f"  ✗ Not aligned (error: {angle_deg:+.2f}°)")
    else:
        print("  ✗ No wall detected")

    robot.stop()

    print()
    print("=" * 70)
    print("Phase 3 Complete!")
    print("=" * 70)
    print()
    print("Verify:")
    print("  ✓ Robot is parallel to right wall")
    print("  ✓ Alignment process was smooth")
    print("  ✓ Final angle error < 2°")


if __name__ == "__main__":
    main()
