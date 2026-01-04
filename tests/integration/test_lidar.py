#!/usr/bin/env python3
"""
Test RPLidar C1 component.

This script tests the lidar in standalone mode and shows how to use it.
"""

import time
from evabot.components.sensors import RPLidarC1


def test_standalone_lidar():
    """Test lidar in standalone mode."""
    print("=" * 60)
    print("RPLidar C1 Standalone Test")
    print("=" * 60)
    print()

    # Create lidar component
    print("Creating RPLidarC1...")
    lidar = RPLidarC1()
    print()

    # Start lidar
    print("Starting lidar...")
    lidar.start()
    print()

    # Wait for scan data to accumulate
    print("Waiting for scan data (3 seconds)...")
    time.sleep(3)
    print()

    # Test basic distance readings
    print("=" * 60)
    print("Basic Distance Readings:")
    print("=" * 60)
    print("  Coordinate System: CW rotation (0°=front, 90°=right, 180°=back, 270°=left)")
    print()
    print(f"  Front (0°):   {lidar.front:.2f}m" if lidar.front else "  Front (0°):   No reading")
    print(f"  Right (90°):  {lidar.right:.2f}m" if lidar.right else "  Right (90°):  No reading")
    print(f"  Back (180°):  {lidar.back:.2f}m" if lidar.back else "  Back (180°):  No reading")
    print(f"  Left (270°):  {lidar.left:.2f}m" if lidar.left else "  Left (270°):  No reading")
    print()

    # Test specific angle
    print("=" * 60)
    print("Specific Angle Readings:")
    print("=" * 60)
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        dist = lidar.get_distance_at(angle)
        if dist:
            print(f"  {angle:3d}°: {dist:.2f}m")
        else:
            print(f"  {angle:3d}°: No reading")
    print()

    # Test angular range
    print("=" * 60)
    print("Angular Range Analysis:")
    print("=" * 60)

    # Front sector (±45°)
    front_min = lidar.get_min_distance_in_range(315, 45)
    if front_min:
        print(f"  Front sector (315°-45°):  min={front_min:.2f}m")

    # Left sector
    left_min = lidar.get_min_distance_in_range(45, 135)
    if left_min:
        print(f"  Left sector (45°-135°):   min={left_min:.2f}m")

    # Back sector
    back_min = lidar.get_min_distance_in_range(135, 225)
    if back_min:
        print(f"  Back sector (135°-225°):  min={back_min:.2f}m")

    # Right sector
    right_min = lidar.get_min_distance_in_range(225, 315)
    if right_min:
        print(f"  Right sector (225°-315°): min={right_min:.2f}m")
    print()

    # Full scan statistics
    print("=" * 60)
    print("Full Scan Statistics:")
    print("=" * 60)
    scan = lidar.scan
    if scan:
        distances = list(scan.values())
        print(f"  Total points: {len(scan)}")
        print(f"  Min distance: {min(distances):.2f}m")
        print(f"  Max distance: {max(distances):.2f}m")
        print(f"  Avg distance: {sum(distances)/len(distances):.2f}m")
        print(f"  Coverage:     {len(scan)/360*100:.1f}%")
    else:
        print("  No scan data available")
    print()

    # Continuous monitoring
    print("=" * 60)
    print("Continuous Monitoring (5 seconds)")
    print("=" * 60)
    print("Press Ctrl+C to stop early")
    print()

    try:
        for i in range(50):  # 5 seconds at 10 Hz
            # Show distances
            front = lidar.front
            right = lidar.right
            left = lidar.left

            status = f"[{i/10:.1f}s] "
            if front:
                status += f"F:{front:.2f}m  "
            if right:
                status += f"R:{right:.2f}m  "
            if left:
                status += f"L:{left:.2f}m"

            print(status)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\nStopped by user")

    print()

    # Stop lidar
    print("Stopping lidar...")
    lidar.stop()
    print()

    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


def test_obstacle_detection():
    """Test obstacle detection logic."""
    print("\n" + "=" * 60)
    print("Obstacle Detection Test")
    print("=" * 60)
    print()

    lidar = RPLidarC1()
    lidar.start()

    print("Waiting for scan data...")
    time.sleep(2)
    print()

    # Simple obstacle detection
    SAFE_DISTANCE = 0.5  # meters

    print(f"Checking for obstacles within {SAFE_DISTANCE}m...")
    print()

    front = lidar.front
    right = lidar.right
    left = lidar.left

    if front and front < SAFE_DISTANCE:
        print(f"⚠️  OBSTACLE AHEAD! ({front:.2f}m at 0°)")
    else:
        print(f"✅ Front (0°) clear: {front:.2f}m" if front else "❓ No front reading")

    if right and right < SAFE_DISTANCE:
        print(f"⚠️  OBSTACLE RIGHT! ({right:.2f}m at 90°)")
    else:
        print(f"✅ Right (90°) clear: {right:.2f}m" if right else "❓ No right reading")

    if left and left < SAFE_DISTANCE:
        print(f"⚠️  OBSTACLE LEFT! ({left:.2f}m at 270°)")
    else:
        print(f"✅ Left (270°) clear: {left:.2f}m" if left else "❓ No left reading")

    print()
    lidar.stop()


if __name__ == '__main__':
    try:
        test_standalone_lidar()
        test_obstacle_detection()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup singleton
        from evabot.hardware import LidarDevice
        LidarDevice.cleanup_all()
        print("\n[Cleanup: Lidar singleton released]")
