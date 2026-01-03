#!/usr/bin/env python3
"""
Lesson 3.6: Track Position - SOLUTION
=====================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot import Robot, MecanumDrive


def print_pose(robot, label=""):
    """Helper function to print current pose nicely"""
    pose = robot.odom.pose
    vel = robot.odom.velocity
    print(f"{label}")
    print(f"  Position: x={pose.x:6.3f}m, y={pose.y:6.3f}m, theta={pose.theta:6.3f}rad ({pose.theta*57.3:6.1f}°)")
    print(f"  Velocity: vx={vel.vx:5.2f}m/s, vy={vel.vy:5.2f}m/s, vtheta={vel.vtheta:5.2f}rad/s")


def main():
    print("=" * 60)
    print("Lesson 3.6: Track Position!")
    print("=" * 60)
    print()

    # Create robot with mecanum drive
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.start()

    time.sleep(0.5)  # Let odometry stabilize

    print_pose(robot, "Starting position:")
    input("Press Enter to start movement...")
    print()

    # ========== Test 1: Forward ==========
    print("Test 1: Driving forward 0.3 m/s for 3 seconds")
    print("(Watch X increase!)")
    print()

    robot.drive.forward(0.3)

    # Monitor position every 0.5 seconds
    for i in range(6):
        time.sleep(0.5)
        print_pose(robot, f"  {(i+1)*0.5:.1f}s:")

    robot.drive.halt()
    time.sleep(1)

    print()

    # ========== Test 2: Strafe Left ==========
    print("Test 2: Strafing left 0.3 m/s for 3 seconds")
    print("(Watch Y increase!)")
    print()

    robot.drive.strafe_left(0.3)

    # Monitor position
    for i in range(6):
        time.sleep(0.5)
        print_pose(robot, f"  {(i+1)*0.5:.1f}s:")

    robot.drive.halt()
    time.sleep(1)

    print()

    # ========== Test 3: Rotate ==========
    print("Test 3: Rotating CCW 0.5 rad/s for 4 seconds")
    print("(Watch Theta increase!)")
    print()

    robot.drive.rotate_ccw(0.5)

    # Monitor position
    for i in range(8):
        time.sleep(0.5)
        print_pose(robot, f"  {(i+1)*0.5:.1f}s:")

    robot.drive.halt()
    time.sleep(1)

    print()
    print("=" * 60)
    print_pose(robot, "Final position:")
    print("=" * 60)

    print()
    print("Shutting down...")
    robot.stop()

    print()
    print("=" * 60)
    print("Excellent! You mastered odometry tracking!")
    print("=" * 60)


if __name__ == "__main__":
    main()
