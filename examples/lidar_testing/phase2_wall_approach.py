#!/usr/bin/env python3
"""
Phase 2: Wall Approach and Stopping (All Directions)

Tests approaching walls in all directions and stopping at the correct distance.

Arena Configuration:
- Arena size: 60×60cm
- Robot radius: 11cm (0.11m)
- Robot placed in center initially (30cm from each wall)
- Target: Stop at 15cm clearance to avoid collision

Usage:
    robot run examples/lidar_testing/phase2_wall_approach.py

Test Sequence:
1. Forward to wall, then reverse to center
2. Strafe left to wall, then strafe right to center
3. Strafe right to wall, then strafe left to center
4. Backward to wall, then forward to center

Results (verified):
- Stop distances: 14.5-14.9cm (target: 15cm) ✓
- No collisions with 15cm threshold ✓
- All 4 directions working correctly ✓
- Robot returns to approximately center ✓

Issue identified:
- Movement has noticeable jitter (unrelated to lidar scans)
- Likely motor PID or velocity control related
- See phase2.1 for jitter investigation
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1


def approach_wall(robot, angle, vx, vy, stop_distance, update_rate, direction_name):
    """
    Approach wall in given direction until clearance <= stop_distance.

    Args:
        robot: Robot instance
        angle: Lidar angle to check (0=front, 90=right, 180=back, 270=left)
        vx, vy: Movement velocities
        stop_distance: Stop when clearance reaches this distance
        update_rate: Loop update rate in Hz
        direction_name: Human-readable direction name for display

    Returns:
        Final clearance distance in meters
    """
    print()
    print(f"Approaching {direction_name} wall...")
    print("─" * 70)
    print(f"{'Time':>6} │ {'Clearance':>21} │ {'Status':>20}")
    print("─" * 70)

    start_time = time.time()
    final_clearance = None

    while True:
        elapsed = time.time() - start_time

        # Check clearance
        clearance = robot.lidar.get_clearance(angle=angle, robot_width=0.22)

        time_str = f"{elapsed:.1f}s"

        if clearance is not None:
            clearance_str = f"{clearance:.3f}m ({clearance*100:.1f}cm)"

            if clearance <= stop_distance:
                # Stop - we're at the wall!
                robot.drive.halt()
                status = "STOPPED"
                print(f"{time_str:>6} │ {clearance_str:>21} │ {status:>20}")
                final_clearance = clearance
                break
            else:
                # Keep moving
                robot.drive.move(vx=vx, vy=vy)
                status = f"Moving {direction_name}"
                print(f"{time_str:>6} │ {clearance_str:>21} │ {status:>20}")
        else:
            # No data - stop for safety
            robot.drive.halt()
            clearance_str = "No data"
            status = "STOPPED - No data"
            print(f"{time_str:>6} │ {clearance_str:>21} │ {status:>20}")
            break

        time.sleep(1.0 / update_rate)

    print("─" * 70)
    return final_clearance


def move_timed(robot, vx, vy, duration, direction_name):
    """Move in direction for specified duration."""
    print()
    print(f"Returning to center ({direction_name})...")
    robot.drive.move(vx=vx, vy=vy)
    time.sleep(duration)
    robot.drive.halt()
    print(f"✓ Moved for {duration:.1f}s")
    time.sleep(1.0)  # Pause between movements


def main():
    print("=" * 70)
    print("Phase 2: Wall Approach and Stopping (All Directions)")
    print("=" * 70)
    print()
    print("Arena: 60×60cm, Robot radius: 11cm")
    print("Place robot in CENTER of arena")
    print()
    print("Test sequence:")
    print("  1. Forward → Reverse to center")
    print("  2. Strafe left → Strafe right to center")
    print("  3. Strafe right → Strafe left to center")
    print("  4. Backward → Forward to center")
    print()
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Configuration
    ARENA_SIZE = 0.60  # 60cm
    ROBOT_RADIUS = 0.11  # 11cm
    STOP_DISTANCE = 0.15  # Stop at 15cm to avoid collision (4cm safety margin)
    SPEED = 0.08  # 8cm/s - slow and safe
    CENTER_DISTANCE = (
        0.15  # Distance from center to wall stop point (30cm - 15cm = 15cm)
    )
    RETURN_TIME = CENTER_DISTANCE / SPEED  # Time to return to center
    UPDATE_RATE = 10  # Hz

    # Initialize robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern="X")
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()

    print()
    print("Waiting for lidar to initialize...")
    time.sleep(3)

    results = []

    try:
        # Test 1: Forward and back
        print()
        print("=" * 70)
        print("TEST 1: Forward → Reverse")
        print("=" * 70)
        dist = approach_wall(
            robot,
            angle=0,
            vx=SPEED,
            vy=0,
            stop_distance=STOP_DISTANCE,
            update_rate=UPDATE_RATE,
            direction_name="forward",
        )
        results.append(("Forward", dist))
        move_timed(
            robot, vx=-SPEED, vy=0, duration=RETURN_TIME, direction_name="reverse"
        )

        # Test 2: Strafe left and back
        print()
        print("=" * 70)
        print("TEST 2: Strafe Left → Strafe Right")
        print("=" * 70)
        dist = approach_wall(
            robot,
            angle=270,
            vx=0,
            vy=SPEED,
            stop_distance=STOP_DISTANCE,
            update_rate=UPDATE_RATE,
            direction_name="left",
        )
        results.append(("Left", dist))
        move_timed(
            robot, vx=0, vy=-SPEED, duration=RETURN_TIME, direction_name="strafe right"
        )

        # Test 3: Strafe right and back
        print()
        print("=" * 70)
        print("TEST 3: Strafe Right → Strafe Left")
        print("=" * 70)
        dist = approach_wall(
            robot,
            angle=90,
            vx=0,
            vy=-SPEED,
            stop_distance=STOP_DISTANCE,
            update_rate=UPDATE_RATE,
            direction_name="right",
        )
        results.append(("Right", dist))
        move_timed(
            robot, vx=0, vy=SPEED, duration=RETURN_TIME, direction_name="strafe left"
        )

        # Test 4: Backward and forward
        print()
        print("=" * 70)
        print("TEST 4: Backward → Forward")
        print("=" * 70)
        dist = approach_wall(
            robot,
            angle=180,
            vx=-SPEED,
            vy=0,
            stop_distance=STOP_DISTANCE,
            update_rate=UPDATE_RATE,
            direction_name="backward",
        )
        results.append(("Backward", dist))
        move_timed(
            robot, vx=SPEED, vy=0, duration=RETURN_TIME, direction_name="forward"
        )

    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")

    # Ensure stopped
    robot.drive.halt()
    time.sleep(0.5)
    robot.stop()

    print()
    print("=" * 70)
    print("Phase 2 Complete!")
    print("=" * 70)
    print()
    print("Results:")
    for direction, distance in results:
        if distance:
            print(f"  {direction:>8}: Stopped at {distance*100:.1f}cm")
        else:
            print(f"  {direction:>8}: No data")
    print()
    print("Expected: ~15cm stop distance in all directions")
    print("Verify robot returned to approximately center position")


if __name__ == "__main__":
    main()
