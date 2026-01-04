#!/usr/bin/env python3
"""
Test Orbbec Camera component.

This script tests the camera in standalone mode and shows how to use it.

Requirements:
- Orbbec 3D camera connected via USB
- PyOrbbecSDK installed (pip install pyorbbecsdk2)
- Proper USB permissions (udev rules)
"""

import time
import numpy as np
from evabot.components.sensors import OrbbecCamera


def test_standalone_camera():
    """Test camera in standalone mode."""
    print("=" * 60)
    print("Orbbec Camera Standalone Test")
    print("=" * 60)
    print()

    # Create camera component
    print("Creating OrbbecCamera...")
    camera = OrbbecCamera(
        rgb_width=640,
        rgb_height=480,
        depth_width=640,
        depth_height=480,
        fps=30
    )
    print()

    # Start camera
    print("Starting camera...")
    try:
        camera.start()
    except Exception as e:
        print(f"❌ Failed to start camera: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check camera is connected via USB")
        print("2. Install udev rules: see PyOrbbecSDK docs")
        print("3. Install PyOrbbecSDK: pip install pyorbbecsdk2")
        return
    print()

    # Wait for frames to accumulate
    print("Waiting for frames (2 seconds)...")
    time.sleep(2)
    print()

    # Test basic frame retrieval
    print("=" * 60)
    print("Basic Frame Retrieval:")
    print("=" * 60)

    rgb = camera.image
    depth = camera.depth
    depth_m = camera.depth_meters

    if rgb is not None:
        print(f"✅ RGB image: {rgb.shape} dtype={rgb.dtype}")
        print(f"   Range: {rgb.min()}-{rgb.max()}")
    else:
        print("❌ No RGB image available")

    if depth is not None:
        print(f"✅ Depth image: {depth.shape} dtype={depth.dtype}")
        print(f"   Range: {depth.min()}-{depth.max()} mm")
    else:
        print("❌ No depth image available")

    if depth_m is not None:
        # Filter out zero values for statistics
        valid_depth = depth_m[depth_m > 0]
        if len(valid_depth) > 0:
            print(f"✅ Depth (meters): {depth_m.shape} dtype={depth_m.dtype}")
            print(f"   Range: {valid_depth.min():.2f}-{valid_depth.max():.2f} m")
            print(f"   Mean:  {valid_depth.mean():.2f} m")
        else:
            print("⚠️  Depth image available but all values are zero")
    else:
        print("❌ No depth (meters) available")

    print()

    # Test depth_at specific points
    print("=" * 60)
    print("Depth at Specific Points:")
    print("=" * 60)

    if depth is not None:
        height, width = depth.shape
        test_points = [
            (width // 2, height // 2, "center"),
            (width // 4, height // 2, "left"),
            (3 * width // 4, height // 2, "right"),
            (width // 2, height // 4, "top"),
            (width // 2, 3 * height // 4, "bottom"),
        ]

        for x, y, name in test_points:
            distance = camera.depth_at(x, y)
            if distance is not None:
                print(f"  {name:8s} ({x:3d}, {y:3d}): {distance:.2f} m")
            else:
                print(f"  {name:8s} ({x:3d}, {y:3d}): No reading")
    else:
        print("  No depth data available")

    print()

    # Test atomically getting both frames
    print("=" * 60)
    print("Atomic Frame Retrieval:")
    print("=" * 60)

    rgb, depth = camera.get_frames()
    if rgb is not None and depth is not None:
        print(f"✅ Both frames retrieved atomically")
        print(f"   RGB:   {rgb.shape}")
        print(f"   Depth: {depth.shape}")
    else:
        print(f"⚠️  Frames: RGB={'available' if rgb is not None else 'missing'}, "
              f"Depth={'available' if depth is not None else 'missing'}")

    print()

    # Display camera info
    print("=" * 60)
    print("Camera Configuration:")
    print("=" * 60)
    print(f"  RGB Resolution:   {camera.resolution_rgb[0]}x{camera.resolution_rgb[1]}")
    print(f"  Depth Resolution: {camera.resolution_depth[0]}x{camera.resolution_depth[1]}")
    print(f"  Frame Rate:       {camera.frame_rate} fps")
    print(f"  Is Connected:     {camera.is_connected}")
    print()

    # Continuous monitoring
    print("=" * 60)
    print("Continuous Monitoring (5 seconds)")
    print("=" * 60)
    print("Press Ctrl+C to stop early")
    print()

    try:
        for i in range(50):  # 5 seconds at 10 Hz
            rgb = camera.image
            depth_m = camera.depth_meters

            status = f"[{i/10:.1f}s] "

            if rgb is not None:
                status += f"RGB: {rgb.shape}  "
            else:
                status += f"RGB: None  "

            if depth_m is not None:
                valid = depth_m[depth_m > 0]
                if len(valid) > 0:
                    status += f"Depth: {valid.min():.2f}-{valid.max():.2f}m"
                else:
                    status += f"Depth: No valid readings"
            else:
                status += f"Depth: None"

            print(status)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nStopped by user")

    print()

    # Stop camera
    print("Stopping camera...")
    camera.stop()
    print()

    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


def test_camera_visualization():
    """Test camera with OpenCV visualization (if available)."""
    try:
        import cv2
        HAS_OPENCV = True
    except ImportError:
        HAS_OPENCV = False

    if not HAS_OPENCV:
        print()
        print("=" * 60)
        print("Visualization Test Skipped")
        print("=" * 60)
        print("Install OpenCV to visualize camera: pip install opencv-python")
        return

    print()
    print("=" * 60)
    print("Camera Visualization Test")
    print("=" * 60)
    print("Press 'q' to quit")
    print()

    camera = OrbbecCamera()

    try:
        camera.start()
        time.sleep(1)  # Wait for first frames

        print("Displaying camera feed...")
        print("Press 'q' in the window to quit")

        while True:
            rgb, depth = camera.get_frames()

            # Display RGB
            if rgb is not None:
                cv2.imshow('RGB', rgb)

            # Display Depth (normalized)
            if depth is not None:
                # Normalize depth for visualization
                depth_viz = depth.copy()
                depth_viz[depth_viz == 0] = depth_viz.max()  # Set invalid to max
                depth_viz = (depth_viz / depth_viz.max() * 255).astype(np.uint8)
                depth_colored = cv2.applyColorMap(depth_viz, cv2.COLORMAP_JET)
                cv2.imshow('Depth', depth_colored)

            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.033)  # ~30 FPS

    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        print("Camera stopped")


if __name__ == '__main__':
    try:
        test_standalone_camera()
        test_camera_visualization()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup singleton
        from evabot.hardware import CameraDevice
        CameraDevice.cleanup_all()
        print("\n[Cleanup: Camera singleton released]")
