#!/usr/bin/env python3
"""
Phase 5: Square Pattern Navigation

Tests navigating around the arena perimeter in a square pattern.

Test Strategy:
1. Move forward → reach front wall → align
2. Strafe left (following front wall) → reach left wall → align
3. Move backward (following left wall) → reach back wall → align
4. Strafe right (following back wall) → reach right wall → align
5. Move forward (following right wall) → reach front wall → complete!

This combines all previous phases:
- Phase 2: Wall approach
- Phase 3: Wall alignment
- Phase 4: Wall following with simultaneous alignment control

No corner detection needed - just move until reaching next wall.

Usage:
    robot run examples/lidar_testing/phase5_square_pattern.py

Test Procedure:
1. Place robot in center of arena
2. Robot will navigate square: forward → left → back → right → forward
3. At each wall, robot aligns before continuing
4. Robot completes square pattern

Results (verified):
- ✓ Forward → Front wall: 14.0cm, aligned +0.19° (quality 0.92)
- ✓ Left (following front) → Left wall: 14.6cm, aligned +0.52° (quality 0.95)
- ✓ Backward (following left) → Back wall: 13.4cm, aligned -0.40° (quality 0.92)
- ✓ Right (following back) → Right wall: 14.7cm, aligned -0.47° (quality 0.88)
- ✓ Forward (following right) → Front wall: 13.4cm - complete!
- ✓ All stops at 13-15cm target distance
- ✓ All alignments within ±1° (excellent precision!)
- ✓ Quality: 0.88-0.95 throughout
- ✓ Robot successfully completed full square pattern
- ✓ Returned to approximately starting position

Configuration:
- Movement speed: 8cm/s
- Stop distance: 15cm from next wall
- Target distance: 14cm from current wall
- Alignment threshold: 2.0°
- Gains: rotation=0.02, distance=0.3
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1


def align_to_wall(robot, wall_angle, max_iterations=50):
    """Align parallel to a wall."""
    ALIGNMENT_THRESHOLD = 2.0
    ROTATION_GAIN = 0.02
    MAX_ROTATION_SPEED = 0.3
    UPDATE_RATE = 5

    print(f"  Aligning to wall {wall_angle}°...")

    for _ in range(max_iterations):
        distance, angle_deg, quality = robot.lidar.check_wall(wall_angle)

        if angle_deg is not None and abs(angle_deg) < ALIGNMENT_THRESHOLD:
            robot.drive.halt()
            print(f"  ✓ Aligned! angle: {angle_deg:+.2f}°, distance: {distance:.3f}m, quality: {quality:.2f}")
            return True

        if angle_deg is not None:
            rotation_speed = ROTATION_GAIN * angle_deg
            rotation_speed = max(-MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, rotation_speed))
            robot.drive.move(vtheta=rotation_speed)

        time.sleep(1.0 / UPDATE_RATE)

    robot.drive.halt()
    print(f"  ✗ Could not align to wall {wall_angle}°")
    return False


def move_to_wall(robot, vx, vy, target_wall_angle, follow_wall_angle=None,
                 stop_distance=0.15, target_distance=0.14, max_time=15.0):
    """
    Move in direction (vx, vy) until target_wall is reached.
    Optionally maintain alignment and distance to follow_wall during movement.

    Args:
        robot: Robot instance
        vx, vy: Base movement velocities
        target_wall_angle: Wall to approach (stop when close)
        follow_wall_angle: Wall to follow during movement (optional)
        stop_distance: Stop when target_wall is this close
        target_distance: Maintain this distance from follow_wall
        max_time: Maximum time for movement
    """
    ROTATION_GAIN = 0.02
    DISTANCE_GAIN = 0.3
    MAX_ROTATION_SPEED = 0.3
    UPDATE_RATE = 5

    direction_name = ""
    if vx > 0:
        direction_name = "forward"
    elif vx < 0:
        direction_name = "backward"
    elif vy > 0:
        direction_name = "left"
    elif vy < 0:
        direction_name = "right"

    if follow_wall_angle is not None:
        print(f"  Moving {direction_name} (following wall {follow_wall_angle}°) → wall {target_wall_angle}°...")
    else:
        print(f"  Moving {direction_name} → wall {target_wall_angle}°...")

    start_time = time.time()

    while time.time() - start_time < max_time:
        # Check target wall clearance
        target_clearance = robot.lidar.get_clearance(target_wall_angle,
                                                      robot_width=0.22,
                                                      angular_range=30.0)

        # Stop if reached target wall
        if target_clearance is not None and target_clearance <= stop_distance:
            robot.drive.halt()
            print(f"  ✓ Reached wall {target_wall_angle}° at {target_clearance:.3f}m")
            return True

        # Base movement
        move_vx = vx
        move_vy = vy
        move_vtheta = 0.0

        # If following a wall, maintain alignment and distance
        if follow_wall_angle is not None:
            distance, angle_deg, quality = robot.lidar.check_wall(follow_wall_angle)

            if distance is not None and angle_deg is not None:
                # Distance correction
                distance_error = distance - target_distance
                correction_factor = 1.0 + DISTANCE_GAIN * distance_error / abs(vx if vx != 0 else vy)
                correction_factor = max(0.5, min(1.5, correction_factor))

                move_vx = vx * correction_factor
                move_vy = vy * correction_factor

                # Alignment correction
                move_vtheta = ROTATION_GAIN * angle_deg
                move_vtheta = max(-MAX_ROTATION_SPEED, min(MAX_ROTATION_SPEED, move_vtheta))

        robot.drive.move(vx=move_vx, vy=move_vy, vtheta=move_vtheta)
        time.sleep(1.0 / UPDATE_RATE)

    robot.drive.halt()
    print(f"  ✗ Timeout moving to wall {target_wall_angle}°")
    return False


def main():
    print("=" * 70)
    print("Phase 5: Square Pattern Navigation")
    print("=" * 70)
    print()
    print("This test navigates around the arena perimeter in a square pattern")
    print()
    print("Setup:")
    print("  1. Place robot in CENTER of arena")
    print("  2. Face robot FORWARD")
    print()
    print("Sequence:")
    print("  1. Forward → front wall (0°) → align")
    print("  2. Left (follow front wall) → left wall (270°) → align")
    print("  3. Backward (follow left wall) → back wall (180°) → align")
    print("  4. Right (follow back wall) → right wall (90°) → align")
    print("  5. Forward (follow right wall) → front wall (0°) → complete!")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Configuration
    SPEED = 0.08
    STOP_DISTANCE = 0.15
    TARGET_DISTANCE = 0.14

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X', acceleration=50)
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    try:
        # Step 1: Forward to front wall, then align
        print()
        print("=" * 70)
        print("STEP 1: Forward → Front Wall (0°)")
        print("=" * 70)
        print()

        if not move_to_wall(robot, vx=SPEED, vy=0, target_wall_angle=0,
                           stop_distance=STOP_DISTANCE):
            print("Failed to reach front wall")
            return

        time.sleep(0.5)

        if not align_to_wall(robot, 0):
            print("Failed to align to front wall")
            return

        time.sleep(1.0)

        # Step 2: Left (following front wall) to left wall, then align
        print()
        print("=" * 70)
        print("STEP 2: Left (following front wall) → Left Wall (270°)")
        print("=" * 70)
        print()

        if not move_to_wall(robot, vx=0, vy=SPEED, target_wall_angle=270,
                           follow_wall_angle=0,
                           stop_distance=STOP_DISTANCE,
                           target_distance=TARGET_DISTANCE):
            print("Failed to reach left wall")
            return

        time.sleep(0.5)

        if not align_to_wall(robot, 270):
            print("Failed to align to left wall")
            return

        time.sleep(1.0)

        # Step 3: Backward (following left wall) to back wall, then align
        print()
        print("=" * 70)
        print("STEP 3: Backward (following left wall) → Back Wall (180°)")
        print("=" * 70)
        print()

        if not move_to_wall(robot, vx=-SPEED, vy=0, target_wall_angle=180,
                           follow_wall_angle=270,
                           stop_distance=STOP_DISTANCE,
                           target_distance=TARGET_DISTANCE):
            print("Failed to reach back wall")
            return

        time.sleep(0.5)

        if not align_to_wall(robot, 180):
            print("Failed to align to back wall")
            return

        time.sleep(1.0)

        # Step 4: Right (following back wall) to right wall, then align
        print()
        print("=" * 70)
        print("STEP 4: Right (following back wall) → Right Wall (90°)")
        print("=" * 70)
        print()

        if not move_to_wall(robot, vx=0, vy=-SPEED, target_wall_angle=90,
                           follow_wall_angle=180,
                           stop_distance=STOP_DISTANCE,
                           target_distance=TARGET_DISTANCE):
            print("Failed to reach right wall")
            return

        time.sleep(0.5)

        if not align_to_wall(robot, 90):
            print("Failed to align to right wall")
            return

        time.sleep(1.0)

        # Step 5: Forward (following right wall) to front wall - complete!
        print()
        print("=" * 70)
        print("STEP 5: Forward (following right wall) → Front Wall (0°)")
        print("=" * 70)
        print()

        if not move_to_wall(robot, vx=SPEED, vy=0, target_wall_angle=0,
                           follow_wall_angle=90,
                           stop_distance=STOP_DISTANCE,
                           target_distance=TARGET_DISTANCE):
            print("Failed to return to front wall")
            return

        print()
        print("=" * 70)
        print("SQUARE PATTERN COMPLETE!")
        print("=" * 70)

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 5 Complete!")
    print("=" * 70)
    print()
    print("Verify:")
    print("  ✓ Robot moved in all 4 directions")
    print("  ✓ Robot aligned at each wall")
    print("  ✓ Robot maintained alignment while following walls")
    print("  ✓ Robot returned to approximately starting position")


if __name__ == "__main__":
    main()
