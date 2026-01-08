#!/usr/bin/env python3
"""
Phase 4: Basic Wall Following

Tests combined wall approach, alignment, and following behavior.

Test Strategy:
1. Move forward to approach front wall
2. Align parallel to front wall
3. Strafe left while maintaining alignment and distance from front wall
4. Stop when reaching left wall

This combines all previous phases:
- Phase 2: Wall approach using get_clearance()
- Phase 3: Alignment using check_wall()
- New: Simultaneous distance and alignment control during strafing

Usage:
    robot run examples/lidar_testing/phase4_wall_following.py

Test Procedure:
1. Place robot in center of arena, facing forward
2. Robot will move forward to front wall
3. Robot will align parallel to front wall
4. Robot will strafe left while maintaining alignment with front wall
5. Robot will stop at left wall

Results (verified):
- ✓ Approached from 39.7cm → 13.6cm (target: 14cm)
- ✓ Aligned from +6.11° → +1.21° in 0.6 seconds
- ✓ Strafed 40.7cm → 14.1cm left clearance (3.5 seconds)
- ✓ Maintained 14.8-16.3cm from front wall during strafing
- ✓ Alignment stayed within ±2.5° throughout strafing
- ✓ Final alignment: -0.20° (nearly perfect!)
- ✓ Quality: 0.72-0.93 (good to excellent)
- ✓ Combined distance and alignment control working smoothly

Configuration:
- Approach speed: 8cm/s
- Strafe speed: 8cm/s
- Target distance from front wall: 14cm
- Alignment threshold: 2.0°
- Rotation gain: 0.02
- Distance gain: 0.3
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1


def main():
    print("=" * 70)
    print("Phase 4: Basic Wall Following")
    print("=" * 70)
    print()
    print("This test demonstrates combined wall approach, alignment, and following")
    print()
    print("Setup:")
    print("  1. Place robot in CENTER of arena")
    print("  2. Face robot FORWARD (toward front wall)")
    print("  3. Robot will approach, align, and strafe along wall")
    print()
    print("Test sequence:")
    print("  1. Move forward to front wall (~14cm)")
    print("  2. Align parallel to front wall")
    print("  3. Strafe left while maintaining alignment with front wall")
    print("  4. Stop at left wall (~15cm)")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Configuration
    ROBOT_RADIUS = 0.11  # 11cm
    APPROACH_DISTANCE = 0.14  # Approach to 14cm from wall (close but safe)
    TARGET_DISTANCE = 0.14  # Maintain ~14cm during strafing
    STOP_DISTANCE = 0.15  # Stop at 15cm from left wall
    APPROACH_SPEED = 0.08  # 8cm/s - slow and safe
    STRAFE_SPEED = 0.08  # 8cm/s strafing
    ALIGNMENT_THRESHOLD = 2.0  # Stop when error < 2 degrees
    ROTATION_GAIN = 0.02  # Proportional control gain
    DISTANCE_GAIN = 0.3  # Gain for distance correction
    MAX_ROTATION_SPEED = 0.3  # Max rotation speed (rad/s)
    UPDATE_RATE = 5  # Hz
    MAX_ITERATIONS = 200  # Safety limit

    # Angles
    FORWARD = 0  # Forward direction
    FRONT_WALL = 0  # Front wall (0°) - wall we approach
    LEFT_WALL = 270  # Left wall (270°)

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X', acceleration=50)
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    print()
    print("=" * 70)
    print("PHASE 1: APPROACH FRONT WALL")
    print("=" * 70)
    print()

    start_time = time.time()
    iteration = 0

    try:
        # Phase 1: Move forward to approach right wall
        while iteration < MAX_ITERATIONS:
            elapsed = time.time() - start_time
            iteration += 1

            # Check clearance forward
            clearance = robot.lidar.get_clearance(FORWARD, robot_width=ROBOT_RADIUS * 2, angular_range=30.0)

            if clearance is not None and clearance > APPROACH_DISTANCE:
                # Keep moving forward
                robot.drive.move(vx=APPROACH_SPEED)
                if iteration % 5 == 0:  # Print every 5 iterations
                    print(f"[{elapsed:.1f}s] Moving forward... clearance: {clearance:.3f}m ({clearance*100:.1f}cm)")
            elif clearance is not None:
                # Reached target distance
                robot.drive.halt()
                print(f"[{elapsed:.1f}s] ✓ Reached wall at {clearance:.3f}m ({clearance*100:.1f}cm)")
                break
            else:
                # No clearance data
                robot.drive.halt()
                print(f"[{elapsed:.1f}s] ✗ No clearance data")
                break

            time.sleep(1.0 / UPDATE_RATE)

        time.sleep(1.0)

        print()
        print("=" * 70)
        print("PHASE 2: ALIGN WITH FRONT WALL")
        print("=" * 70)
        print()

        # Phase 2: Align with front wall
        iteration = 0
        while iteration < MAX_ITERATIONS:
            elapsed = time.time() - start_time
            iteration += 1

            # Check wall alignment
            distance, angle_deg, quality = robot.lidar.check_wall(FRONT_WALL)

            if distance is not None and angle_deg is not None:
                if abs(angle_deg) < ALIGNMENT_THRESHOLD:
                    robot.drive.halt()
                    print(f"[{elapsed:.1f}s] ✓ ALIGNED! angle: {angle_deg:+.2f}°, distance: {distance:.3f}m, quality: {quality:.2f}")
                    break
                else:
                    # Proportional rotation control
                    rotation_speed = ROTATION_GAIN * angle_deg
                    rotation_speed = max(-MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, rotation_speed))
                    robot.drive.move(vtheta=rotation_speed)
                    if iteration % 5 == 0:
                        print(f"[{elapsed:.1f}s] Aligning... angle: {angle_deg:+.2f}°, rotating: {rotation_speed:+.3f} rad/s")
            else:
                robot.drive.halt()
                print(f"[{elapsed:.1f}s] ✗ No wall detected")
                break

            time.sleep(1.0 / UPDATE_RATE)

        time.sleep(1.0)

        print()
        print("=" * 70)
        print("PHASE 3: STRAFE LEFT WITH ALIGNMENT")
        print("=" * 70)
        print()
        print(f"{'Time':>6} │ {'Left Clear':>11} │ {'Front Dist':>11} │ {'Angle':>7} │ {'Quality':>7} │ {'Action':>25}")
        print("─" * 70)

        # Phase 3: Strafe left while maintaining alignment and distance
        iteration = 0
        while iteration < MAX_ITERATIONS:
            elapsed = time.time() - start_time
            iteration += 1

            # Check left wall clearance
            left_clearance = robot.lidar.get_clearance(LEFT_WALL, robot_width=ROBOT_RADIUS * 2, angular_range=30.0)

            # Check front wall alignment and distance
            distance, angle_deg, quality = robot.lidar.check_wall(FRONT_WALL)

            time_str = f"{elapsed:.1f}s"
            left_str = f"{left_clearance:.3f}m" if left_clearance is not None else "---"
            right_str = f"{distance:.3f}m" if distance is not None else "---"
            angle_str = f"{angle_deg:+.2f}°" if angle_deg is not None else "---"
            quality_str = f"{quality:.2f}" if quality is not None else "---"

            # Check if reached left wall
            if left_clearance is not None and left_clearance <= STOP_DISTANCE:
                robot.drive.halt()
                action = "REACHED LEFT WALL!"
                print(f"{time_str:>6} │ {left_str:>11} │ {right_str:>11} │ {angle_str:>7} │ {quality_str:>7} │ {action:>25}")
                break

            # Combined control: strafe + align + maintain distance
            if distance is not None and angle_deg is not None and left_clearance is not None:
                # Base strafing speed (left = positive vy)
                vy = STRAFE_SPEED

                # Distance correction (proportional to error from target)
                # If too close to front wall, slow down or stop strafing
                # If too far, speed up strafing
                distance_error = distance - TARGET_DISTANCE
                vy += DISTANCE_GAIN * distance_error

                # Clamp vy to reasonable range
                vy = max(0.0, min(STRAFE_SPEED * 1.5, vy))

                # Alignment correction (rotation)
                rotation_speed = ROTATION_GAIN * angle_deg
                rotation_speed = max(-MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, rotation_speed))

                # Execute combined movement
                robot.drive.move(vy=vy, vtheta=rotation_speed)
                action = f"vy={vy:.3f}, vθ={rotation_speed:+.3f}"
                print(f"{time_str:>6} │ {left_str:>11} │ {right_str:>11} │ {angle_str:>7} │ {quality_str:>7} │ {action:>25}")
            else:
                robot.drive.halt()
                action = "No sensor data"
                print(f"{time_str:>6} │ {left_str:>11} │ {right_str:>11} │ {angle_str:>7} │ {quality_str:>7} │ {action:>25}")
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

    # Final status check
    print()
    print("Final status:")
    left_clearance = robot.lidar.get_clearance(LEFT_WALL, robot_width=ROBOT_RADIUS * 2, angular_range=30.0)
    distance, angle_deg, quality = robot.lidar.check_wall(FRONT_WALL)

    if left_clearance is not None:
        print(f"  Left clearance:  {left_clearance:.3f}m ({left_clearance*100:.1f}cm)")
    if distance is not None:
        print(f"  Front distance:  {distance:.3f}m ({distance*100:.1f}cm)")
    if angle_deg is not None:
        print(f"  Alignment:       {angle_deg:+.2f}°")
    if quality is not None:
        print(f"  Quality:         {quality:.2f}")

    robot.stop()

    print()
    print("=" * 70)
    print("Phase 4 Complete!")
    print("=" * 70)
    print()
    print("Verify:")
    print("  ✓ Robot approached front wall smoothly")
    print("  ✓ Robot aligned parallel to front wall")
    print("  ✓ Robot maintained alignment with front wall during strafing")
    print("  ✓ Robot stopped at left wall")


if __name__ == "__main__":
    main()
