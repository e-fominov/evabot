#!/usr/bin/env python3
"""
Progressive wall following tests for 60×60cm maze.

Tests robot's ability to:
1. Approach and stop before wall (clearance checking)
2. Align with wall (two-point method)
3. Drive while maintaining alignment
4. Maintain distance from wall (strafe control)
5. Detect and navigate openings
6. Follow wall using right-hand rule

Robot: 20×20cm
Maze: 60×60cm with 30×30cm cells
Clearance: 5cm per side when centered
"""

from evabot import Robot, MecanumDrive, RPLidarC1
import time
import math


def test_1_approach_and_stop(robot):
    """
    Test 1: Approach wall and stop using rectangular clearance.

    Drive forward slowly, continuously checking clearance.
    Stop when too close (15cm safety threshold).
    """
    print("\n" + "=" * 60)
    print("TEST 1: Approach and Stop Before Wall")
    print("=" * 60)
    print("Robot will drive forward and stop 15cm before obstacle.")
    print("Press Enter to start...")
    input()

    try:
        print("\nDriving forward...")
        while True:
            clearance = robot.lidar.get_clearance(0)  # Check forward

            if clearance is None:
                print("No lidar data!")
                break

            print(f"  Forward clearance: {clearance:.3f}m", end='\r')

            if clearance < 0.15:  # Stop threshold
                print(f"\n  Stopping! Clearance: {clearance:.3f}m")
                robot.drive.halt()
                break

            robot.drive.forward(0.1)  # Slow speed
            time.sleep(0.02)

    except KeyboardInterrupt:
        robot.drive.halt()
        print("\nTest interrupted")

    robot.drive.halt()
    print("\nTest 1 complete. Robot stopped before wall.")
    print("Press Enter to continue...")
    input()


def test_2_align_stationary(robot):
    """
    Test 2: Align parallel to right wall (stationary).

    Use two-point measurement to detect angle error.
    Rotate slowly until aligned (error < 1cm).
    """
    print("\n" + "=" * 60)
    print("TEST 2: Align with Right Wall (Stationary)")
    print("=" * 60)
    print("Position robot near right wall (not at corner).")
    print("Robot will rotate until parallel.")
    print("Press Enter to start...")
    input()

    try:
        print("\nAligning with right wall...")
        iteration = 0

        while iteration < 100:  # Max iterations
            wall_info = robot.lidar.check_wall(90)  # Right wall

            if wall_info is None:
                print("  No wall detected! Check position or at corner.")
                break

            distance, angle_error = wall_info
            print(f"  Wall: {distance:.3f}m, Error: {angle_error:+.4f}m", end='\r')

            if abs(angle_error) < 0.01:  # 1cm threshold
                print(f"\n  Aligned! Final error: {angle_error:+.4f}m")
                robot.drive.halt()
                break

            # Proportional control
            K = 0.3
            turn_speed = K * angle_error
            turn_speed = max(-0.2, min(0.2, turn_speed))  # Clamp

            robot.drive.move(vtheta=turn_speed)
            time.sleep(0.02)
            iteration += 1

        else:
            print("\n  Reached max iterations")

    except KeyboardInterrupt:
        robot.drive.halt()
        print("\nTest interrupted")

    robot.drive.halt()
    print("\nTest 2 complete. Robot aligned with wall.")
    print("Press Enter to continue...")
    input()


def test_3_drive_while_aligned(robot):
    """
    Test 3: Drive forward while maintaining alignment with right wall.

    Move forward at constant speed while continuously correcting
    alignment using proportional control.
    """
    print("\n" + "=" * 60)
    print("TEST 3: Drive While Maintaining Alignment")
    print("=" * 60)
    print("Position robot parallel to right wall.")
    print("Robot will drive forward while staying aligned.")
    print("Press Enter to start...")
    input()

    try:
        print("\nDriving forward with alignment control...")

        while True:
            # Check forward clearance
            front_clear = robot.lidar.get_clearance(0)
            if front_clear is None or front_clear < 0.15:
                print(f"\n  Stopping! Front clearance: {front_clear:.3f}m")
                robot.drive.halt()
                break

            # Check alignment with right wall
            wall_info = robot.lidar.check_wall(90)

            if wall_info is None:
                print("\n  Lost wall! Stopping.")
                robot.drive.halt()
                break

            distance, angle_error = wall_info
            print(f"  Front: {front_clear:.3f}m, Wall: {distance:.3f}m, Error: {angle_error:+.4f}m", end='\r')

            # Alignment correction
            K = 0.3
            turn_speed = K * angle_error
            turn_speed = max(-0.3, min(0.3, turn_speed))

            robot.drive.move(vx=0.1, vtheta=turn_speed)
            time.sleep(0.02)

    except KeyboardInterrupt:
        robot.drive.halt()
        print("\nTest interrupted")

    robot.drive.halt()
    print("\nTest 3 complete. Robot maintained alignment while moving.")
    print("Press Enter to continue...")
    input()


def test_4_maintain_distance(robot):
    """
    Test 4: Maintain distance from wall while driving.

    Drive forward while:
    - Maintaining alignment (rotate)
    - Maintaining 15cm distance from wall (strafe)
    """
    print("\n" + "=" * 60)
    print("TEST 4: Maintain Distance While Following Wall")
    print("=" * 60)
    print("Position robot parallel to right wall at any distance.")
    print("Robot will drive forward while maintaining 15cm from wall.")
    print("Press Enter to start...")
    input()

    target_distance = 0.15  # 15cm from wall

    try:
        print(f"\nFollowing wall at {target_distance:.2f}m distance...")

        while True:
            # Check forward clearance
            front_clear = robot.lidar.get_clearance(0)
            if front_clear is None or front_clear < 0.15:
                print(f"\n  Stopping! Front clearance: {front_clear:.3f}m")
                robot.drive.halt()
                break

            # Check wall
            wall_info = robot.lidar.check_wall(90)

            if wall_info is None:
                print("\n  Lost wall! Stopping.")
                robot.drive.halt()
                break

            distance, angle_error = wall_info

            # Distance control (strafe)
            dist_error = distance - target_distance
            K_strafe = 0.5
            strafe_speed = -K_strafe * dist_error  # Negative: right is negative vy
            strafe_speed = max(-0.1, min(0.1, strafe_speed))

            # Alignment control (rotate)
            K_turn = 0.3
            turn_speed = K_turn * angle_error
            turn_speed = max(-0.3, min(0.3, turn_speed))

            print(f"  Front: {front_clear:.3f}m, Dist: {distance:.3f}m, Align: {angle_error:+.4f}m", end='\r')

            robot.drive.move(vx=0.1, vy=strafe_speed, vtheta=turn_speed)
            time.sleep(0.02)

    except KeyboardInterrupt:
        robot.drive.halt()
        print("\nTest interrupted")

    robot.drive.halt()
    print("\nTest 4 complete. Robot maintained distance from wall.")
    print("Press Enter to continue...")
    input()


def test_5_detect_and_turn(robot):
    """
    Test 5: Detect opening and turn into it.

    Follow wall until right clearance increases (opening detected),
    then turn 90° right into the opening.
    """
    print("\n" + "=" * 60)
    print("TEST 5: Detect Opening and Turn")
    print("=" * 60)
    print("Position robot before a right turn (opening on right).")
    print("Robot will follow wall, detect opening, and turn right.")
    print("Press Enter to start...")
    input()

    target_distance = 0.15

    try:
        print("\nFollowing wall, watching for opening...")

        while True:
            # Check forward clearance
            front_clear = robot.lidar.get_clearance(0)
            if front_clear is None or front_clear < 0.15:
                print(f"\n  Front blocked: {front_clear:.3f}m")
                robot.drive.halt()
                break

            # Check right clearance (opening detection)
            right_clear = robot.lidar.get_clearance(90)

            if right_clear is not None and right_clear > 0.25:
                print(f"\n  Opening detected! Right clearance: {right_clear:.3f}m")
                print("  Turning right...")
                robot.drive.halt()
                time.sleep(0.5)
                robot.drive.move_by(dtheta=-math.pi/2)  # Turn right 90°
                print("  Turn complete!")
                break

            # Follow wall normally
            wall_info = robot.lidar.check_wall(90)

            if wall_info is None:
                # No wall - might already be at opening
                print("\n  No wall detected")
                robot.drive.halt()
                break

            distance, angle_error = wall_info

            # Distance and alignment control
            dist_error = distance - target_distance
            strafe_speed = -0.5 * dist_error
            strafe_speed = max(-0.1, min(0.1, strafe_speed))

            turn_speed = 0.3 * angle_error
            turn_speed = max(-0.3, min(0.3, turn_speed))

            print(f"  Front: {front_clear:.3f}m, Right: {right_clear:.3f}m, Wall: {distance:.3f}m", end='\r')

            robot.drive.move(vx=0.1, vy=strafe_speed, vtheta=turn_speed)
            time.sleep(0.02)

    except KeyboardInterrupt:
        robot.drive.halt()
        print("\nTest interrupted")

    robot.drive.halt()
    print("\nTest 5 complete. Robot detected opening and turned.")
    print("Press Enter to continue...")
    input()


def test_6_right_hand_rule(robot):
    """
    Test 6: Full right-hand rule maze navigation.

    Continuously:
    - Check right for opening → turn right
    - Check front for wall → turn left
    - Otherwise → follow right wall

    Runs indefinitely (Ctrl-C to stop).
    """
    print("\n" + "=" * 60)
    print("TEST 6: Right-Hand Rule Maze Navigation")
    print("=" * 60)
    print("Position robot in maze.")
    print("Robot will follow right wall indefinitely using right-hand rule.")
    print("Press Ctrl-C to stop.")
    print("Press Enter to start...")
    input()

    target_distance = 0.15

    try:
        print("\nNavigating maze with right-hand rule...")
        print("(Right wall priority, turn right at openings, left at dead ends)\n")

        while True:
            front_clear = robot.lidar.get_clearance(0)
            right_clear = robot.lidar.get_clearance(90)

            # Decision logic
            if right_clear is not None and right_clear > 0.25:
                # Opening on right - turn right
                print("\n→ Right opening detected, turning right...")
                robot.drive.halt()
                time.sleep(0.3)
                robot.drive.move_by(dtheta=-math.pi/2)
                time.sleep(0.3)

            elif front_clear is None or front_clear < 0.20:
                # Wall ahead - turn left
                print("\n← Wall ahead, turning left...")
                robot.drive.halt()
                time.sleep(0.3)
                robot.drive.move_by(dtheta=math.pi/2)
                time.sleep(0.3)

            else:
                # Follow right wall
                wall_info = robot.lidar.check_wall(90)

                if wall_info is None:
                    # No wall on right, drift right slowly
                    print("  No right wall, searching...", end='\r')
                    robot.drive.move(vx=0.08, vy=-0.03)  # Drift right
                    time.sleep(0.02)
                    continue

                distance, angle_error = wall_info

                # 3-DOF control: forward + strafe + rotate
                dist_error = distance - target_distance
                strafe_speed = -0.5 * dist_error
                strafe_speed = max(-0.1, min(0.1, strafe_speed))

                turn_speed = 0.3 * angle_error
                turn_speed = max(-0.3, min(0.3, turn_speed))

                print(f"  Following | Front: {front_clear:.2f}m | Right: {right_clear:.2f}m | Wall: {distance:.2f}m", end='\r')

                robot.drive.move(vx=0.08, vy=strafe_speed, vtheta=turn_speed)
                time.sleep(0.02)

    except KeyboardInterrupt:
        robot.drive.halt()
        print("\n\nMaze navigation stopped by user")

    robot.drive.halt()
    print("\nTest 6 complete. Right-hand rule navigation tested.")


def main():
    print("=" * 60)
    print("Wall Following Test Suite")
    print("=" * 60)
    print("Testing progressive wall following behaviors")
    print("Maze: 60×60cm, Robot: 20×20cm")
    print()

    # Create robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.lidar = RPLidarC1()
    robot.start()

    time.sleep(2)  # Wait for sensors to initialize

    try:
        # Run all tests
        test_1_approach_and_stop(robot)
        test_2_align_stationary(robot)
        test_3_drive_while_aligned(robot)
        test_4_maintain_distance(robot)
        test_5_detect_and_turn(robot)
        test_6_right_hand_rule(robot)

        print("\n" + "=" * 60)
        print("All tests complete!")
        print("=" * 60)

    finally:
        robot.stop()


if __name__ == "__main__":
    main()
