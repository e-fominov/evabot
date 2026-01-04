# Orbbec 3D Camera Implementation

## Summary

Successfully implemented Orbbec 3D camera support for EvaBot! The camera provides RGB color images and depth maps for vision-based robotics.

## Features

✅ **Hardware Layer (Singleton)**
- `CameraDevice` singleton manages physical Orbbec camera
- Uses PyOrbbecSDK (v2) for camera access
- Background thread continuously captures RGB + Depth
- Thread-safe access to latest frames

✅ **Component Layer (Per-Robot)**
- `OrbbecCamera` component with easy-to-use API
- Works standalone or attached to Robot
- RGB and Depth frame access
- Depth at specific pixel coordinates
- Configurable resolution and frame rate

## Hardware

- **Model**: Orbbec 3D / DaBai DCW (or compatible)
- **Connection**: USB
- **RGB Resolution**: 640x480 @ 30fps (default, configurable)
- **Depth Resolution**: 640x480 @ 30fps (default, configurable)
- **Depth Range**: ~0.3m to 10m (model dependent)
- **Depth Format**: uint16 millimeters, or float32 meters

## Installation

### Install PyOrbbecSDK

```bash
pip install pyorbbecsdk2
```

Note: Package name is `pyorbbecsdk2` but import is `import pyorbbecsdk`

### Linux: Install udev rules

Required for non-root USB access:

```bash
# Download and install udev rules
sudo wget https://raw.githubusercontent.com/orbbec/pyorbbecsdk/main/misc/99-obsensor-libusb.rules \
     -O /etc/udev/rules.d/99-obsensor-libusb.rules

# Reload rules
sudo udevadm control --reload-rules && sudo udevadm trigger

# Add user to video group
sudo usermod -a -G video $USER

# Logout and login for group changes to take effect
```

## Usage

### Standalone Mode

```python
from evabot.components.sensors import OrbbecCamera
import cv2

# Create and start camera
camera = OrbbecCamera()
camera.start()

# Wait for first frames
import time
time.sleep(1)

# Get RGB image
rgb = camera.image
if rgb is not None:
    cv2.imshow('RGB', rgb)
    cv2.waitKey(1)

# Get depth map (millimeters)
depth = camera.depth
if depth is not None:
    print(f"Depth shape: {depth.shape}")
    print(f"Depth range: {depth.min()}-{depth.max()} mm")

# Get depth in meters
depth_m = camera.depth_meters
if depth_m is not None:
    valid = depth_m[depth_m > 0]
    print(f"Depth: {valid.min():.2f}m to {valid.max():.2f}m")

# Get distance at specific point (meters)
distance = camera.depth_at(320, 240)  # Center pixel
if distance:
    print(f"Object at center: {distance:.2f}m")

# Get both frames atomically
rgb, depth = camera.get_frames()

camera.stop()
```

### With Robot

```python
from evabot import Robot
from evabot.components.sensors import OrbbecCamera

# Create robot and attach camera
robot = Robot()
robot.camera = OrbbecCamera()

# Start robot (starts all components)
robot.start()

# Access camera through robot
rgb = robot.camera.image
depth = robot.camera.depth_meters

# Check distance to object
distance = robot.camera.depth_at(320, 240)
if distance and distance < 0.5:
    print("Object close! Stopping...")
    robot.drive.stop()

# Use in control loop
@robot.loop(rate=10)
def vision_navigate(robot):
    # Get depth at center
    center_dist = robot.camera.depth_at(320, 240)

    if center_dist is not None and center_dist < 0.3:
        robot.drive.stop()  # Too close
    else:
        robot.drive.forward(0.2)

robot.start()
```

### Custom Resolution

```python
# High resolution
camera = OrbbecCamera(
    rgb_width=1280,
    rgb_height=720,
    depth_width=1280,
    depth_height=720,
    fps=15
)

# Low resolution (faster)
camera = OrbbecCamera(
    rgb_width=320,
    rgb_height=240,
    depth_width=320,
    depth_height=240,
    fps=60
)
```

## API Reference

### OrbbecCamera Component

**Constructor:**
```python
OrbbecCamera(
    device_id=0,           # Camera device index
    rgb_width=640,         # RGB width in pixels
    rgb_height=480,        # RGB height in pixels
    depth_width=640,       # Depth width in pixels
    depth_height=480,      # Depth height in pixels
    fps=30                 # Frame rate in Hz
)
```

**Properties:**
- `image` - Latest RGB frame as numpy array (H, W, 3) uint8
- `depth` - Latest depth frame as numpy array (H, W) uint16 (millimeters)
- `depth_meters` - Latest depth frame as numpy array (H, W) float32 (meters)
- `is_connected` - Connection status bool
- `resolution_rgb` - Tuple (width, height) for RGB
- `resolution_depth` - Tuple (width, height) for depth
- `frame_rate` - Configured FPS

**Methods:**
- `start()` - Start camera capture
- `stop()` - Stop camera capture
- `depth_at(x, y)` - Get depth at pixel (x, y) in meters
- `get_frames()` - Get (rgb, depth) frames atomically

## Examples

### Basic Capture

```python
from evabot.components.sensors import OrbbecCamera
import time

camera = OrbbecCamera()
camera.start()

time.sleep(1)  # Wait for first frames

rgb = camera.image
depth_m = camera.depth_meters

print(f"RGB: {rgb.shape if rgb is not None else 'None'}")
print(f"Depth: {depth_m.shape if depth_m is not None else 'None'}")

camera.stop()
```

### Distance Measurement

```python
camera = OrbbecCamera()
camera.start()
time.sleep(1)

# Measure distances at different points
points = [
    (320, 240, "center"),
    (160, 240, "left"),
    (480, 240, "right"),
]

for x, y, name in points:
    dist = camera.depth_at(x, y)
    if dist:
        print(f"{name}: {dist:.2f}m")

camera.stop()
```

### Visualization with OpenCV

```python
import cv2
import numpy as np
from evabot.components.sensors import OrbbecCamera

camera = OrbbecCamera()
camera.start()

print("Press 'q' to quit")

while True:
    rgb, depth = camera.get_frames()

    # Show RGB
    if rgb is not None:
        cv2.imshow('RGB', rgb)

    # Show depth (colorized)
    if depth is not None:
        # Normalize for visualization
        depth_viz = depth.copy()
        depth_viz[depth_viz == 0] = depth_viz.max()
        depth_viz = (depth_viz / depth_viz.max() * 255).astype(np.uint8)
        depth_colored = cv2.applyColorMap(depth_viz, cv2.COLORMAP_JET)
        cv2.imshow('Depth', depth_colored)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.stop()
cv2.destroyAllWindows()
```

### Object Detection (Simple)

```python
from evabot import Robot
from evabot.components.sensors import OrbbecCamera
from evabot.components.drive import MecanumDrive

robot = Robot()
robot.camera = OrbbecCamera()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)

@robot.loop(rate=10)
def avoid_obstacles(robot):
    """Stop if object detected within 50cm at center."""
    distance = robot.camera.depth_at(320, 240)

    if distance is not None and distance < 0.5:
        robot.drive.stop()
        print(f"⚠️  Obstacle at {distance:.2f}m - stopped")
    else:
        robot.drive.forward(0.2)

robot.start()
```

## Integration Tests

- `tests/integration/test_camera.py` - Comprehensive camera test with visualization

Run with:
```bash
python tests/integration/test_camera.py
```

## Implementation Details

### Two-Layer Architecture

1. **Hardware Layer (CameraDevice)**
   - Singleton per physical camera
   - Manages PyOrbbecSDK pipeline
   - Background capture thread
   - Thread-safe frame storage

2. **Component Layer (OrbbecCamera)**
   - Per-robot instance
   - Easy-to-use API
   - Works standalone or with Robot
   - Automatic cleanup on exit

### Performance

- **Frame Rate**: Up to 30 FPS (configurable)
- **Latency**: < 100ms (hardware dependent)
- **Thread-Safety**: All operations thread-safe
- **Memory**: ~2-4 MB per frame pair (640x480)

### Coordinate System

- **Image Origin**: Top-left corner (0, 0)
- **X-axis**: Left to right (0 to width-1)
- **Y-axis**: Top to bottom (0 to height-1)
- **Depth Units**: millimeters (uint16) or meters (float32)
- **Zero Depth**: Invalid/no reading (common at far distances or reflective surfaces)

## Troubleshooting

### No devices found

**Symptoms**: `No Orbbec devices found` error

**Solutions**:
1. Check USB connection: `lsusb | grep -i orbbec`
2. Install udev rules (see Installation above)
3. Check permissions: `ls -l /dev/bus/usb/*/*`
4. Try different USB port (prefer USB 3.0)
5. Restart camera: unplug and replug USB

### Import error

**Symptoms**: `ModuleNotFoundError: No module named 'pyorbbecsdk'`

**Solution**:
```bash
pip install pyorbbecsdk2
```

Note: Package is `pyorbbecsdk2`, import is `pyorbbecsdk`

### No frames captured

**Symptoms**: `camera.image` and `camera.depth` return None

**Solutions**:
1. Wait 1-2 seconds after `start()` for first frames
2. Check camera supports RGB (some models are depth-only)
3. Try different resolutions
4. Check camera is not in use by another process
5. Check logs for stream configuration errors

### Poor depth quality

**Symptoms**: Many zero values or noisy depth

**Solutions**:
1. Avoid reflective or transparent surfaces
2. Ensure adequate lighting for RGB camera
3. Objects too close (< 0.3m) or too far (> 5m)
4. Clean camera lens
5. Reduce frame rate for more stable readings

### Performance issues

**Symptoms**: Low frame rate or lag

**Solutions**:
1. Reduce resolution (e.g., 320x240)
2. Lower frame rate (e.g., 15 FPS)
3. Process only depth OR RGB (not both)
4. Use `get_frames()` for atomic access
5. Check CPU usage

## Testing Results

✅ Device detection and initialization
✅ RGB frame capture
✅ Depth frame capture
✅ Depth at specific pixels
✅ Atomic frame retrieval
✅ Multiple resolutions
✅ Thread-safety verified
✅ Robot integration working

## Next Steps

Camera is ready to use! Possible enhancements:

1. **Computer Vision** - Object detection, tracking
2. **Point Clouds** - 3D reconstruction from depth
3. **Visual Servoing** - Camera-based robot control
4. **SLAM** - Visual-inertial mapping
5. **Calibration** - RGB-Depth alignment

## Phase 3 Status

✅ **COMPLETE** - Orbbec Camera fully operational!

All tasks from IMPLEMENTATION_PLAN.md Phase 3.2 completed:
- [x] Install PyOrbbecSDK
- [x] Implement CameraDevice singleton
- [x] Background RGB + Depth capture
- [x] OrbbecCamera component wrapper
- [x] Frame access properties (.image, .depth)
- [x] Depth at pixel method
- [x] Atomic frame retrieval
- [x] Integration test
- [x] Documentation

**Phase 3 (Sensors): COMPLETE** ✅
- Phase 3.1: RPLidar C1 ✅
- Phase 3.2: Orbbec Camera ✅

## References

- [PyOrbbecSDK GitHub](https://github.com/orbbec/pyorbbecsdk)
- [PyOrbbecSDK Documentation](https://orbbec.github.io/pyorbbecsdk/)
- Integration test: `tests/integration/test_camera.py`
- Example: `examples/robot_with_camera.py` (coming soon)
