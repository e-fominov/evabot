#!/usr/bin/env python3
"""
Example: Robot with Orbbec Camera

Demonstrates using the Orbbec 3D camera with a robot for
simple obstacle avoidance using depth information.

Hardware required:
- Orbbec 3D camera (USB connected)
- MecanumDrive robot (4x Servo42D motors)
"""

import time
from evabot import Robot
from evabot.components.drive import MecanumDrive
from evabot.components.sensors import OrbbecCamera


def example_basic_camera():
    """Basic camera usage with robot."""
    print("=" * 60)
    print("Example 1: Basic Camera Access")
    print("=" * 60)
    print()

    # Create robot with camera
    robot = Robot()
    robot.camera = OrbbecCamera()

    # Start robot (starts camera too)
    robot.start()

    # Wait for first frames
    print("Waiting for camera frames...")
    time.sleep(2)
    print()

    # Access camera data
    rgb = robot.camera.image
    depth_m = robot.camera.depth_meters

    if rgb is not None:
        print(f"✅ RGB image: {rgb.shape}")
    else:
        print("❌ No RGB image")

    if depth_m is not None:
        valid = depth_m[depth_m > 0]
        if len(valid) > 0:
            print(f"✅ Depth range: {valid.min():.2f}m to {valid.max():.2f}m")
        else:
            print("⚠️  Depth available but no valid readings")
    else:
        print("❌ No depth image")

    print()

    # Check distance at center
    distance = robot.camera.depth_at(320, 240)
    if distance is not None:
        print(f"Distance at center: {distance:.2f}m")
    else:
        print("No distance reading at center")

    print()

    # Stop robot
    robot.stop()
    print("✅ Example complete")
    print()


def example_obstacle_detection():
    """Use camera for obstacle detection."""
    print("=" * 60)
    print("Example 2: Obstacle Detection with Camera")
    print("=" * 60)
    print()

    # Create robot with camera (no drive for this example)
    robot = Robot()
    robot.camera = OrbbecCamera()

    robot.start()
    time.sleep(2)

    # Monitor for obstacles
    SAFE_DISTANCE = 0.5  # meters

    print(f"Checking for obstacles within {SAFE_DISTANCE}m...")
    print("Monitoring 5 points across image")
    print()

    # Check multiple points
    width, height = robot.camera.resolution_depth
    points = [
        (width // 4, height // 2, "left"),
        (width // 2 - 50, height // 2, "center-left"),
        (width // 2, height // 2, "center"),
        (width // 2 + 50, height // 2, "center-right"),
        (3 * width // 4, height // 2, "right"),
    ]

    for x, y, name in points:
        dist = robot.camera.depth_at(x, y)
        if dist is not None:
            if dist < SAFE_DISTANCE:
                print(f"⚠️  {name:12s}: {dist:.2f}m - OBSTACLE!")
            else:
                print(f"✅ {name:12s}: {dist:.2f}m - clear")
        else:
            print(f"❓ {name:12s}: No reading")

    print()
    robot.stop()
    print("✅ Example complete")
    print()


def example_vision_behavior():
    """Simple vision-based behavior."""
    print("=" * 60)
    print("Example 3: Vision-Based Robot Behavior")
    print("=" * 60)
    print()

    # Create robot with camera and drive
    robot = Robot()
    robot.camera = OrbbecCamera()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)

    # Define behavior
    @robot.loop(rate=10)
    def vision_navigate(robot):
        """
        Navigate using camera:
        - Check depth at center of image
        - Stop if object too close
        - Otherwise drive forward slowly
        """
        # Get distance at center
        distance = robot.camera.depth_at(320, 240)

        if distance is None:
            # No reading - stop to be safe
            robot.drive.stop()
            print("[No depth reading - stopped]")

        elif distance < 0.3:
            # Too close - stop
            robot.drive.stop()
            print(f"[Obstacle at {distance:.2f}m - stopped]")

        elif distance < 0.5:
            # Getting close - slow down
            robot.drive.forward(0.1)
            print(f"[Object at {distance:.2f}m - slow]")

        else:
            # Clear - move forward
            robot.drive.forward(0.2)
            print(f"[Clear ({distance:.2f}m) - moving]")

    print("Starting vision-based navigation...")
    print("Robot will:")
    print("  - Stop if obstacle within 30cm")
    print("  - Slow down if obstacle within 50cm")
    print("  - Drive forward if clear")
    print()
    print("Press Ctrl+C to stop")
    print()

    try:
        robot.start()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        robot.stop()
        print("✅ Example complete")
        print()


def example_continuous_monitoring():
    """Continuous camera monitoring."""
    print("=" * 60)
    print("Example 4: Continuous Camera Monitoring")
    print("=" * 60)
    print()

    robot = Robot()
    robot.camera = OrbbecCamera()

    robot.start()
    time.sleep(1)

    print("Monitoring camera (10 seconds)")
    print("Press Ctrl+C to stop early")
    print()

    try:
        for i in range(100):
            # Get distance readings across image
            left = robot.camera.depth_at(160, 240)
            center = robot.camera.depth_at(320, 240)
            right = robot.camera.depth_at(480, 240)

            # Format output
            status = f"[{i/10:.1f}s] "

            if left is not None:
                status += f"L:{left:.2f}m  "
            else:
                status += "L:---  "

            if center is not None:
                status += f"C:{center:.2f}m  "
            else:
                status += "C:---  "

            if right is not None:
                status += f"R:{right:.2f}m"
            else:
                status += "R:---"

            print(status)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        robot.stop()
        print()
        print("✅ Example complete")
        print()


if __name__ == '__main__':
    try:
        # Run examples
        example_basic_camera()

        example_obstacle_detection()

        # Uncomment to test with actual robot drive:
        # example_vision_behavior()

        example_continuous_monitoring()

        print()
        print("=" * 60)
        print("All Examples Complete!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        from evabot.hardware import CameraDevice
        CameraDevice.cleanup_all()
        print("\n[Cleanup: Camera singleton released]")
