#!/usr/bin/env python3
"""
Quick test of move_by() method.

Tests basic distance-based movements.
"""

from evabot import Robot, MecanumDrive
import time
import math

def main():
    print("=" * 60)
    print("Testing move_by() Method")
    print("=" * 60)
    print()

    # Create robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.start()

    time.sleep(1)

    print("Starting position:")
    print(f"  x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m, θ={robot.odom.pose.theta:.3f}rad")
    print()

    # Test 1: Forward
    print("Test 1: Move forward 0.5m")
    robot.drive.move_by(dx=0.5, speed=0.2)
    print(f"  Position: x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m")
    time.sleep(1)

    # Test 2: Strafe left
    print("\nTest 2: Strafe left 0.3m")
    robot.drive.move_by(dy=0.3, speed=0.2)
    print(f"  Position: x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m")
    time.sleep(1)

    # Test 3: Rotate
    print("\nTest 3: Rotate 90° CCW")
    robot.drive.move_by(dtheta=math.pi/2, speed=0.2)
    print(f"  Angle: θ={robot.odom.pose.theta:.3f}rad ({math.degrees(robot.odom.pose.theta):.1f}°)")
    time.sleep(1)

    # Test 4: Combined
    print("\nTest 4: Forward + strafe (diagonal)")
    robot.drive.move_by(dx=0.3, dy=0.3, speed=0.2)
    print(f"  Position: x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m")
    time.sleep(1)

    print("\n" + "=" * 60)
    print("Final position:")
    print(f"  x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m, θ={robot.odom.pose.theta:.3f}rad")
    print("=" * 60)

    robot.stop()
    print("\nTest complete!")

if __name__ == "__main__":
    main()
