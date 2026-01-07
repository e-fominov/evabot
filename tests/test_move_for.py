#!/usr/bin/env python3
"""
Quick test of move_for() and zero_position() methods.
"""

from evabot import Robot, MecanumDrive
import time
import math

def main():
    print("=" * 60)
    print("Testing move_for() and zero_position() Methods")
    print("=" * 60)
    print()

    # Create robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.start()

    time.sleep(1)

    # Test 1: zero_position
    print("Test 1: zero_position()")
    print(f"  Before: x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m")
    robot.drive.zero_position()
    print(f"  After:  x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m")
    print()
    time.sleep(1)

    # Test 2: move_for (forward)
    print("Test 2: move_for() - Forward 3 seconds at 0.2 m/s")
    robot.drive.move_for(3.0, vx=0.2)
    print(f"  Position: x={robot.odom.pose.x:.3f}m (expected ~0.6m)")
    print()
    time.sleep(1)

    # Test 3: move_for (strafe)
    print("Test 3: move_for() - Strafe left 2 seconds at 0.15 m/s")
    robot.drive.move_for(2.0, vy=0.15)
    print(f"  Position: x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m")
    print()
    time.sleep(1)

    # Test 4: move_for (rotate)
    print("Test 4: move_for() - Rotate 2 seconds at 0.5 rad/s")
    robot.drive.move_for(2.0, vtheta=0.5)
    print(f"  Angle: θ={robot.odom.pose.theta:.3f}rad ({math.degrees(robot.odom.pose.theta):.1f}°)")
    print()
    time.sleep(1)

    # Test 5: move_for (combined)
    print("Test 5: move_for() - Combined movement 3 seconds")
    robot.drive.move_for(3.0, vx=0.2, vy=0.1, vtheta=0.3)
    print(f"  Position: x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m")
    print(f"  Angle: θ={robot.odom.pose.theta:.3f}rad")
    print()
    time.sleep(1)

    # Test 6: Return to origin test
    print("Test 6: Return to origin test")
    print(f"  Current: x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m")

    # Try to return to origin
    print("  Attempting to return...")
    robot.drive.move_by(dx=-robot.odom.pose.x, dy=-robot.odom.pose.y)
    robot.drive.move_by(dtheta=-robot.odom.pose.theta)

    print(f"  Final: x={robot.odom.pose.x:.3f}m, y={robot.odom.pose.y:.3f}m, θ={robot.odom.pose.theta:.3f}rad")
    print("  (Should be close to origin, but not perfect due to drift)")
    print()

    print("=" * 60)
    print("Test complete!")
    print("=" * 60)

    robot.stop()

if __name__ == "__main__":
    main()
