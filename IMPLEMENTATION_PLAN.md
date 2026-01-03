# EvaBot Implementation Plan
**Updated**: 2026-01-03 (Architecture revision)

## Core Architecture

### Two-Layer Design

**Layer 1: Hardware Resources (Singleton)**
- Physical devices shared across all robots
- One instance per physical hardware
- Examples: `CanBus('can0')`, `CameraDevice('/dev/video0')`, `LidarDevice('/dev/ttyUSB0')`

**Layer 2: Robot State (Per-Instance)**
- Each robot has isolated state
- Multiple robots can coexist
- Share hardware layer, independent state

```
Hardware Layer (Singleton):
├── CanBus('can0')               # Physical CAN interface
├── CameraDevice('/dev/video0')  # Physical USB camera
└── LidarDevice('/dev/ttyUSB0')  # Physical lidar

Robot Layer (Per-Instance):
├── Robot 1
│   ├── odom: x=1.0, y=0.5      # Robot 1's state
│   ├── drive: MecanumDrive → uses CanBus singleton
│   └── camera: Camera → uses CameraDevice singleton
│
└── Robot 2
    ├── odom: x=2.0, y=1.5      # Robot 2's state
    ├── drive: MecanumDrive → uses SAME CanBus singleton
    └── camera: Camera → uses SAME CameraDevice singleton
```

### Component Flexibility

**Components work standalone OR with robot:**

```python
# Level 1: Standalone (no robot needed)
from evabot.components.motors import Servo42D
motor = Servo42D(1)
motor.run(30)

# Level 3: With robot (recommended)
from evabot import Robot
from evabot.components.drives import MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
# Motors use CanBus singleton
# Motors update robot.odom state

robot.start()
```

### State Access (Not `.state`!)

**Explicit, frame-aware access:**

```python
# Direct component access (not robot.state.x!)
robot.odom.x         # meters (odometry frame)
robot.odom.y         # meters
robot.odom.theta     # radians
robot.odom.velocity  # Velocity object

robot.lidar.front    # meters
robot.lidar.scan     # {angle_deg: distance_m}

robot.camera.image   # RGB image
robot.camera.depth   # Depth image

# Future: Multiple frames
robot.odom.x         # Odometry frame (Phase 1-6)
robot.map.x          # Map frame (Phase 7: SLAM)
```

### Control Loops

**Loops receive robot (not state):**

```python
@robot.loop(rate=10)
def navigate(robot):  # Gets full robot!
    if robot.lidar.front < 0.3:  # 30cm = 0.3m
        robot.drive.stop()
    else:
        robot.drive.forward(0.3)
```

### Multiple Robots Support

```python
# Two robots, shared hardware, isolated state
robot1 = Robot()
robot1.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot1.odom.x = 1.0  # Robot 1's position

robot2 = Robot()
robot2.drive = MecanumDrive(fl=8, fr=6, bl=7, br=5)
robot2.odom.x = 2.0  # Robot 2's position (different!)

# Both use SAME CanBus singleton
# But have SEPARATE odometry state
```

---

## Hardware Configuration

### ✅ Confirmed Working
- **Motors**: 4x Servo42D (CAN IDs 1-4) on `can0` at 500kbps
  - Accessible from local host (not just RPi)
  - Internal encoders: 16,384 pulses/rev (0.0153mm resolution)
  - Firmware: V62.0.63
  - 80mm diameter wheels

- **Orbbec 3D Camera**: Orbbec 3D
  - SDK installed: `/home/fm/work/OrbbecSDK`
  - Tools: `/home/fm/work/OrbbecSDK/build/bin`
  - Capabilities: **RGB + Depth** (much better than simple webcam!)
  - Already tested and working

### ⏳ Needs Driver Work
- **RPLidar C1M1-R2**: Detected at `/dev/ttyUSB0`
  - Baud rate: 460800 (not standard 115200)
  - Device info/health readable ✓
  - Scan data parsing needs custom implementation
  - Standard `rplidar-roboticia` library incompatible
  - Will implement custom driver based on Slamtec SDK

## Development Environment

**Location**: `/home/fm/work/evabot`
**Host**: Local machine (fm) with all hardware connected
- CAN adapter on `can0`
- Lidar on `/dev/ttyUSB0`
- Orbbec camera via OrbbecSDK

**No need for SSH to RPi** - All development happens locally!

---

## Phase 1: Foundation (Week 1)
**Goal**: Core architecture and motor control

### 1.1 Project Structure ✅ COMPLETED

```bash
/home/fm/work/evabot/
├── setup.py                 # Package installer ✓
├── README.md                # Project docs ✓
├── IMPLEMENTATION_PLAN.md   # This file ✓
├── evabot/
│   ├── __init__.py          # Main module ✓
│   ├── robot.py             # Robot container ✓
│   ├── state.py             # Thread-safe state ✓
│   ├── hardware/            # Hardware singletons
│   │   ├── __init__.py
│   │   └── can_bus.py       # CanBus singleton
│   └── components/
│       ├── base.py          # Base Component ✓
│       ├── motors/
│       │   ├── __init__.py
│       │   └── servo42d.py  # Servo42D motor
│       ├── drives/
│       ├── sensors/
│       └── actuators/
└── examples/
    └── phase1_test.py       # Working example ✓
```

**Completed**:
- [x] Directory structure
- [x] setup.py
- [x] Base Component class
- [x] Robot class with new state API
- [x] RobotState with frame-aware access (robot.odom.x)
- [x] Package installation (pip install -e .)
- [x] All imports work

**Time**: 3 hours ✓

### 1.2 Hardware Layer - CanBus Singleton

```python
evabot/hardware/can_bus.py
```

**Singleton pattern for shared CAN bus:**

```python
from evabot.hardware import CanBus

# Get default CAN bus (singleton)
bus = CanBus.get_default(channel='can0', bitrate=500000)

# All motors share this bus
```

**API Design**:
```python
class CanBus:
    @classmethod
    def get_default(cls, channel='can0', bitrate=500000):
        """Get or create default CAN bus (singleton)"""

    @classmethod
    def cleanup_all(cls):
        """Cleanup all buses (called on exit)"""
```

**Tasks**:
- [ ] Implement CanBus singleton manager
- [ ] Auto-cleanup on program exit (atexit)
- [ ] Thread-safe instance management
- [ ] Test: Multiple components share same bus

**Time**: 2-3 hours

### 1.3 Servo42D Motor Component

```python
evabot/components/motors/servo42d.py
```

**Based on**: Working `servo42d_control.py` from RPi

**Works standalone OR with robot:**

```python
# Standalone (Level 1)
motor = Servo42D(1)  # Uses CanBus singleton
motor.run(30)
position = motor.get_position()

# With robot (Level 3+)
robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
# Motors created internally
# Use CanBus singleton + update robot.odom
```

**API Design**:
```python
class Servo42D(Component):
    def __init__(self, can_id, can_bus=None):
        """
        CAN motor (Servo42D hardware).

        Args:
            can_id: CAN ID (1-255)
            can_bus: Optional CanBus instance (uses singleton if None)
        """

    def run(self, speed_rpm):
        """Run motor at speed (works standalone)"""

    def stop(self):
        """Stop motor"""

    def get_position(self):
        """Read encoder position (pulses)"""

    def get_speed(self):
        """Read current speed (RPM)"""

    def enable(self):
        """Enable motor"""

    def disable(self):
        """Disable motor"""
```

**Tasks**:
- [ ] Refactor servo42d_control.py → Servo42D class
- [ ] Integrate with CanBus singleton
- [ ] Clean API: `.run()`, `.stop()`, `.get_position()`, `.get_speed()`
- [ ] Works standalone (no robot required)
- [ ] Works with robot (_attach_to_robot updates robot.odom)
- [ ] Handle CAN responses properly
- [ ] Test standalone: `motor = Servo42D(1); motor.run(30)`
- [ ] Test with hardware: Verify CAN communication

**Time**: 6-8 hours

**Deliverable**:
```python
# Level 1: Standalone motor
from evabot.components.motors import Servo42D

motor = Servo42D(1)
motor.enable()
motor.run(30)  # 30 RPM
print(f"Position: {motor.get_position()} pulses")
motor.stop()
motor.disable()
```

---

## Phase 2: Drive Systems (Week 2)
**Goal**: MecanumDrive with odometry

### 2.1 Drive Base Class

```python
evabot/components/drives/base.py
```

**Abstract interface for all drive systems:**

```python
class Drive(Component):
    """Base class for all drive systems"""

    def forward(self, speed):
        """Move forward at speed (m/s)"""
        raise NotImplementedError

    def backward(self, speed):
        """Move backward"""
        raise NotImplementedError

    def stop(self):
        """Stop all motors"""
        raise NotImplementedError
```

**Tasks**:
- [ ] Abstract Drive base class
- [ ] Standard interface definition
- [ ] Velocity conversion helpers
- [ ] Test: Interface compliance

**Time**: 2-3 hours

### 2.2 MecanumDrive Component

```python
evabot/components/drives/mecanum.py
```

**Based on**: Working `mecanum_robot.py` from RPi

**Creates Servo42D motors internally:**

```python
robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
# Internally creates: Servo42D(4), Servo42D(2), etc.
# All motors share CanBus singleton
# All motors update robot.odom when attached

# Usage
robot.drive.forward(0.3)      # m/s
robot.drive.strafe_left(0.2)
robot.drive.rotate(0.5)       # rad/s
robot.drive.drive(vx, vy, vtheta)  # Full 3DOF
```

**API Design**:
```python
class MecanumDrive(Drive):
    def __init__(self, fl, fr, bl, br, wheel_diameter=0.08):
        """
        4-wheel mecanum drive.

        Args:
            fl, fr, bl, br: CAN IDs for motors
            wheel_diameter: Wheel diameter in meters (default 0.08 = 80mm)
        """
        # Internally creates Servo42D instances
        self.motors = {
            'fl': Servo42D(fl),
            'fr': Servo42D(fr),
            'bl': Servo42D(bl),
            'br': Servo42D(br)
        }

    def forward(self, speed):
        """Move forward (m/s)"""

    def backward(self, speed):
        """Move backward (m/s)"""

    def strafe_left(self, speed):
        """Strafe left (m/s)"""

    def strafe_right(self, speed):
        """Strafe right (m/s)"""

    def rotate(self, angular_speed):
        """Rotate in place (rad/s)"""

    def drive(self, vx, vy, vtheta):
        """Full 3DOF control (m/s, m/s, rad/s)"""

    def stop(self):
        """Stop all motors"""
```

**Tasks**:
- [ ] Refactor mecanum_robot.py → MecanumDrive
- [ ] Create Servo42D motors internally
- [ ] All movement methods (forward, backward, strafe, rotate)
- [ ] Full 3DOF control: `.drive(vx, vy, vtheta)`
- [ ] Auto-enable/disable motors (prevent oscillation)
- [ ] Integration with odometry
- [ ] Test: All movement directions

**Time**: 8-10 hours

### 2.3 Odometry Component

```python
evabot/components/drives/odometry.py
```

**Background thread reads encoders, updates robot.odom:**

```python
# Odometry is automatic when using MecanumDrive
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.start()

# Odometry thread runs in background
# Updates robot.odom.x, robot.odom.y, robot.odom.theta
print(f"Position: {robot.odom.x:.3f}m, {robot.odom.y:.3f}m")
```

**API Design**:
```python
class Odometry(Component):
    """
    Background odometry thread.

    Reads motor encoders, updates robot.odom state.
    Automatically created by MecanumDrive.
    """

    def __init__(self, motors, wheel_diameter=0.08, update_rate=50):
        """
        Args:
            motors: Dict of Servo42D motors
            wheel_diameter: Wheel diameter in meters
            update_rate: Update frequency in Hz (default 50)
        """

    def start(self):
        """Start odometry thread"""

    def stop(self):
        """Stop odometry thread"""

    def _odometry_loop(self):
        """Background thread: read encoders, update robot.odom"""
```

**Tasks**:
- [ ] Encoder polling thread (20-50 Hz)
- [ ] Read all 4 motor encoders (command 0x31)
- [ ] Mecanum kinematics: wheels → robot velocity
- [ ] Position integration: velocity → x, y, theta
- [ ] Update robot.odom (if attached to robot)
- [ ] Thread-safe state updates
- [ ] Test: Drive 1m forward, verify position accurate to 5%

**Time**: 8-10 hours

**Deliverable**:
```python
from evabot import Robot
from evabot.components.drives import MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)

robot.start()

# Open-loop
robot.drive.forward(0.3)  # m/s
time.sleep(3)
robot.drive.stop()

print(f"Position: x={robot.odom.x:.3f}m, y={robot.odom.y:.3f}m")
# Should show ~0.9m forward
```

---

## Phase 3: Sensors (Week 3-4)
**Goal**: Lidar and Camera components

### 3.1 RPLidar C1 Component

```python
evabot/components/sensors/lidar.py
evabot/hardware/lidar_device.py
```

**Hardware**: RPLidar C1M1-R2 at `/dev/ttyUSB0`, 460800 baud

**Two-layer design:**

```python
# Hardware layer (singleton)
class LidarDevice:
    @classmethod
    def get_default(cls, port='/dev/ttyUSB0', baudrate=460800):
        """Get or create lidar device (singleton)"""

# Component layer (per-robot)
class RPLidarC1(Component):
    def __init__(self, device=None):
        """RPLidar component (uses LidarDevice singleton)"""

    @property
    def front(self):
        """Distance in front (0°) in meters"""

    @property
    def scan(self):
        """Full 360° scan: {angle_deg: distance_m}"""
```

**Usage:**

```python
# Standalone
from evabot.components.sensors import RPLidarC1
lidar = RPLidarC1()
lidar.start()
print(f"Front: {lidar.front}m")

# With robot
robot = Robot()
robot.lidar = RPLidarC1()
robot.start()
print(f"Front: {robot.lidar.front}m")
```

**Custom Driver Needed**:
- Standard libraries incompatible with C1M1-R2
- Implement based on Slamtec SDK protocol
- Reference: `/home/fm/work/ttc-4/ros2_ws/src/webots_bridge/webots_bridge/lidar_stl19p_node.py`

**Tasks**:
- [ ] Research Slamtec SDK C1 protocol
- [ ] Implement LidarDevice singleton (serial communication, 460800 baud)
- [ ] Parse scan packets
- [ ] Background scan thread
- [ ] RPLidarC1 component wrapper
- [ ] Process scans → `.front`, `.back`, `.left`, `.right`
- [ ] Full scan access: `.scan` (360° dict)
- [ ] Test: Read distances, verify accuracy

**Time**: 10-15 hours (custom driver work)

**Alternative**: Use mock/simulator initially, implement real driver later

### 3.2 Orbbec Camera Component

```python
evabot/components/sensors/camera.py
evabot/hardware/camera_device.py
```

**Hardware**: Orbbec 3D (RGB + Depth)
**SDK**: `/home/fm/work/OrbbecSDK`
**Reference**: `/home/fm/work/ttc-4/ros2_ws/src/orbbec_camera`

**Two-layer design:**

```python
# Hardware layer (singleton)
class CameraDevice:
    @classmethod
    def get_default(cls, sdk_path='/home/fm/work/OrbbecSDK'):
        """Get or create camera device (singleton)"""

# Component layer (per-robot)
class OrbbecCamera(Component):
    def __init__(self, device=None):
        """Orbbec camera component (uses CameraDevice singleton)"""

    @property
    def image(self):
        """Latest RGB frame (numpy array)"""

    @property
    def depth(self):
        """Latest depth frame (numpy array)"""

    def depth_at(self, x, y):
        """Depth at pixel (x, y) in meters"""
```

**Usage:**

```python
robot = Robot()
robot.camera = OrbbecCamera()

robot.start()

# RGB and depth
import cv2
cv2.imshow('RGB', robot.camera.image)
cv2.imshow('Depth', robot.camera.depth)

# Point distance
distance = robot.camera.depth_at(320, 240)
print(f"Center distance: {distance:.2f}m")
```

**Tasks**:
- [ ] Integrate OrbbecSDK (Python bindings or subprocess)
- [ ] CameraDevice singleton (manages physical camera)
- [ ] Background capture thread (configurable FPS, default 30)
- [ ] OrbbecCamera component wrapper
- [ ] `.image` - latest RGB frame
- [ ] `.depth` - latest depth frame
- [ ] `.depth_at(x, y)` - point distance
- [ ] Color detection (HSV thresholding) - optional
- [ ] Test: Capture RGB+Depth, verify frame rate

**Time**: 10-12 hours

**Deliverable**:
```python
from evabot import Robot
from evabot.components.sensors import OrbbecCamera

robot = Robot()
robot.camera = OrbbecCamera()

robot.start()

# Access data
rgb = robot.camera.image
depth = robot.camera.depth
distance = robot.camera.depth_at(320, 240)

print(f"RGB shape: {rgb.shape}")
print(f"Depth at center: {distance:.2f}m")
```

---

## Phase 4: Control Loops (Week 5)
**Goal**: Decorator-based behaviors

### 4.1 Loop Decorator ✅ COMPLETED

Already implemented in robot.py:

```python
@robot.loop(rate=10)
def navigate(robot):  # Gets robot!
    if robot.lidar.front < 0.3:
        robot.drive.stop()
    else:
        robot.drive.forward(0.3)

robot.start()  # Runs loop forever
```

**Features**:
- [x] Fixed-rate execution
- [x] Multiple loops supported
- [x] Passes robot (not state)
- [x] Graceful shutdown (Ctrl+C)

### 4.2 Closed-Loop Motion Control

```python
evabot/components/drives/motion.py
```

**Add to MecanumDrive:**

```python
# Blocking methods (use odometry)
robot.drive.move_forward(1.0)  # 1 meter
robot.drive.move_backward(0.5)
robot.drive.turn_left(90)      # degrees
robot.drive.turn_right(45)

# Drive a square
for _ in range(4):
    robot.drive.move_forward(1.0)
    robot.drive.turn_right(90)
```

**Tasks**:
- [ ] `.move_forward(distance_m)` - uses robot.odom
- [ ] `.move_backward(distance_m)`
- [ ] `.turn_left(degrees)`, `.turn_right(degrees)`
- [ ] Simple PID controller for accuracy
- [ ] Acceleration/deceleration profiles
- [ ] Test: Drive 1m square, measure accuracy

**Time**: 8-10 hours

**Deliverable**:
```python
robot.drive.move_forward(1.0)  # Drive 1 meter
robot.drive.turn_right(90)     # Turn 90 degrees
# Should be within 5% accuracy
```

---

## Phase 5: Actuators (Week 6)
**Goal**: 5th motor for gripper/arm

### 5.1 Servo Actuator Component

```python
evabot/components/actuators/servo.py
```

**Hardware**: Additional Servo42D (CAN ID 5)

**API Design**:
```python
from evabot.components.actuators import ServoActuator

robot.gripper = ServoActuator(can_id=5)

robot.gripper.open()
robot.gripper.close()
robot.gripper.set_position(45)  # degrees
robot.gripper.set_position(45, speed=30)  # with speed control
```

**Tasks**:
- [ ] ServoActuator class (wraps Servo42D for position control)
- [ ] `.set_position(angle)` - move to angle
- [ ] `.set_position(angle, speed)` - controlled movement
- [ ] Gripper preset (open/close positions)
- [ ] Test: Move actuator, read position

**Time**: 4-6 hours

---

## Phase 6: Polish & Examples (Week 7)
**Goal**: Documentation and example programs

### 6.1 Progressive Learning Examples

```python
examples/
```

**Complete learning path:**

```python
# Level 1: Single motor (3 lines!)
from evabot.components.motors import Servo42D
motor = Servo42D(1)
motor.run(30)

# Level 2: Multiple motors
motors = [Servo42D(i) for i in [1,2,3,4]]
for m in motors:
    m.run(30)

# Level 3: Drive system
robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.drive.forward(0.3)

# Level 4: Add sensors
robot.lidar = RPLidarC1()
if robot.lidar.front < 0.3:
    robot.drive.stop()

# Level 5: Behaviors
@robot.loop(rate=10)
def navigate(robot):
    if robot.lidar.front < 0.3:
        robot.drive.rotate(0.5)
    else:
        robot.drive.forward(0.3)
```

**Tasks**:
- [ ] `level1_single_motor.py` - Control one motor
- [ ] `level2_motor_group.py` - Control multiple motors
- [ ] `level3_drive.py` - Use MecanumDrive
- [ ] `level4_lidar.py` - Obstacle avoidance
- [ ] `level5_camera.py` - Object detection
- [ ] `level6_behaviors.py` - Multi-sensor behaviors
- [ ] Test: All examples run successfully

**Time**: 6-8 hours

### 6.2 Documentation

**Tasks**:
- [ ] README with quick start
- [ ] API documentation (docstrings)
- [ ] Tutorial: Level 1 → Level 6 progression
- [ ] Hardware setup guide
- [ ] Architecture explanation (two-layer design)
- [ ] Troubleshooting guide
- [ ] Video demos (optional)

**Time**: 8-10 hours

---

## Phase 7: Advanced Features (Week 8+)
**Goal**: SLAM and autonomous navigation

### 7.1 Map Frame (SLAM)

```python
# Add map frame support
robot.odom.x    # Odometry frame (drifts)
robot.map.x     # Map frame (SLAM-corrected)

# Transform between frames
pose_in_map = robot.odom.pose.to_map_frame()
```

### 7.2 2D SLAM

```python
evabot/slam/mapper.py
```

**Tasks**:
- [ ] Lidar + Odometry fusion
- [ ] 2D occupancy grid mapping
- [ ] Particle filter localization (optional)
- [ ] Map visualization
- [ ] Test: Map a room

**Time**: 15-20 hours

### 7.3 High-Level Behaviors

```python
evabot/behaviors/
```

**Tasks**:
- [ ] Wall following
- [ ] Explore and map
- [ ] Go to goal (A* planning)
- [ ] Object tracking (visual servoing)
- [ ] Test: Autonomous navigation

**Time**: 20-30 hours

---

## Configuration Decisions ✅ FINALIZED

### Units
- **Distance**: **meters** (base unit, can add `.x_cm` helpers later)
- **Angles**: **radians** (base unit, degrees in API where appropriate)
- **Speed**: **m/s** and **rad/s**

### Coordinate System (ROS convention)
- **X**: Forward (front of robot)
- **Y**: Left
- **Z**: Up (for 3D camera)
- **Theta**: Counter-clockwise from X axis (radians)

### Frames
**Limited set (not infinite like ROS2):**
- `robot.odom` - Odometry frame (Phase 1-6)
- `robot.map` - Map frame (Phase 7: SLAM)
- No tf2 tree, just these 2 frames

### Component Naming
- **Servo42D** (not `Motor`) - hardware-specific
- **CanBus** (not `Bus`) - explicit interface
- **RPLidarC1** (not `Lidar`) - hardware-specific
- **OrbbecCamera** (not `Camera`) - hardware-specific

### Robot Role
**Optional but recommended:**
- Not required for Level 1-2 (standalone components)
- Essential for Level 3+ (state tracking, organization)
- Supports multiple robots (each with isolated state)

---

## Milestones & Testing

### Milestone 1 (End of Week 2): Basic Robot
```python
from evabot import Robot
from evabot.components.drives import MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)

robot.drive.forward(0.3)      # m/s
robot.drive.strafe_left(0.2)
robot.drive.rotate(0.5)
robot.drive.stop()

print(f"Position: {robot.odom.x:.3f}m, {robot.odom.y:.3f}m")
```

### Milestone 2 (End of Week 4): Sensors Working
```python
from evabot import Robot
from evabot.components.drives import MecanumDrive
from evabot.components.sensors import RPLidarC1, OrbbecCamera

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.lidar = RPLidarC1()
robot.camera = OrbbecCamera()

robot.start()

print(f"Lidar front: {robot.lidar.front:.2f}m")
print(f"Camera depth at center: {robot.camera.depth_at(320, 240):.2f}m")
```

### Milestone 3 (End of Week 5): Autonomous Behavior
```python
from evabot import Robot
from evabot.components.drives import MecanumDrive
from evabot.components.sensors import RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.lidar = RPLidarC1()

@robot.loop(rate=10)
def navigate(robot):
    if robot.lidar.front < 0.3:
        robot.drive.rotate(0.5)  # Turn
    else:
        robot.drive.forward(0.3)

robot.start()  # Autonomous navigation!
```

---

## Priority Order

### Must Have (MVP) - Weeks 1-2
1. ✅ Project structure
2. ✅ Base classes (Component, Robot)
3. ✅ State system (robot.odom.x, not robot.state.x)
4. 🚧 CanBus singleton
5. 🚧 Servo42D motor component
6. ⏳ MecanumDrive
7. ⏳ Odometry

### Should Have - Weeks 3-5
8. ⏳ RPLidar C1 driver (custom implementation)
9. ⏳ Orbbec camera integration
10. ✅ Loop decorator
11. ⏳ Closed-loop control

### Nice to Have - Weeks 6-7
12. ServoActuator
13. Full documentation
14. Example programs (all 6 levels)

### Future - Week 8+
15. SLAM (map frame)
16. Advanced behaviors
17. Web interface (optional)
18. Simulation mode (optional)

---

## Risk Mitigation

### RPLidar C1 Driver Complexity
**Risk**: Custom driver takes longer than expected
**Mitigation**:
- Implement mock lidar for development
- Add real driver in Phase 3.5 (extra week)
- Use basic distance readings first, full scan later

### Orbbec SDK Integration
**Risk**: Python bindings complex
**Mitigation**:
- Start with C++ tools for testing
- Use subprocess to call SDK tools
- Full Python integration in Phase 3.5

### Multiple CAN Bus Instances
**Risk**: Components accidentally create multiple buses
**Mitigation**:
- CanBus singleton prevents this
- Auto-cleanup on exit
- Clear error messages if bus open fails

### State Synchronization
**Risk**: Thread-safety issues with robot.odom
**Mitigation**:
- RLock on all state access
- Odometry thread owns state updates
- Components read-only access

---

## Success Criteria

### Technical:
- ✅ All 4 motors controllable independently
- ⏳ Mecanum drive works in all directions
- ⏳ Odometry tracks position within 5% error over 1m
- ⏳ Lidar provides 360° scan at 10 Hz
- ⏳ Camera provides RGB+Depth at 15+ FPS
- ⏳ Robot responds to commands in <100ms
- ⏳ Stable operation for 30+ minutes
- ✅ Multiple robots can coexist (shared hardware, isolated state)

### Educational:
- ✅ Kids can control single motor in 3 lines of code
- ✅ Progressive examples work without modification
- ✅ Clear error messages when things go wrong
- ✅ No need to understand threads, locks, or CAN protocol (hidden)
- ⏳ Documentation readable by 12+ year olds

### Maintainability:
- ✅ Modular architecture (swap components easily)
- ✅ Well-documented API (docstrings)
- ✅ Consistent naming conventions
- ✅ Type hints throughout (where appropriate)
- ⏳ Example code for every feature

---

## Next Steps

**Immediate** (Today):
1. ✅ Phase 1.1 complete (project structure, base classes)
2. 🚧 Phase 1.2: Implement CanBus singleton
3. 🚧 Phase 1.3: Implement Servo42D motor component
4. ⏳ Test with real hardware (CAN motors)

**This Week**:
- Complete Phase 1 (CanBus + Servo42D)
- Start Phase 2 (MecanumDrive + Odometry)
- Test basic robot movement

**Next Week**:
- Complete Phase 2
- Begin sensor integration (Lidar or Camera)

---

**Ready to continue with Phase 1.2 - CanBus Singleton!**
