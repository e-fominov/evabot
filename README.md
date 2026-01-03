# EvaBot 🤖

**Simple robotics library for progressive learning**

EvaBot is designed to help kids learn robotics programming from controlling a single motor to building autonomous robots with sensors and behaviors.

## Features

- 🎯 **Progressive Learning**: Start simple, add complexity gradually
- 🧩 **Modular Components**: Mix and match motors, sensors, and behaviors
- 📚 **Kid-Friendly API**: Clear, intuitive commands
- 🚀 **Real Hardware**: Works with Servo42D motors, RPLidar, Orbbec cameras
- 🔧 **No ROS Required**: Simple Python, no complex dependencies

## Quick Start

### Installation

```bash
cd /home/fm/work/evabot
pip install -e .
```

### Level 1: Control a Single Motor

```python
from evabot import Motor

motor = Motor(1)
motor.enable()
motor.run(30)  # 30 RPM
motor.stop()
```

### Level 2: Multiple Motors

```python
from evabot import Motor

motors = [Motor(i) for i in [1, 2, 3, 4]]
for motor in motors:
    motor.enable()
    motor.run(30)
```

### Level 3: Drive System

```python
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)

robot.drive.forward(0.3)  # 0.3 m/s
robot.drive.strafe_left(0.2)
robot.drive.stop()
```

### Level 4: Add Sensors

```python
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.lidar = RPLidarC1()

robot.start()

while True:
    if robot.lidar.front < 30:  # cm
        robot.drive.stop()
    else:
        robot.drive.forward(0.2)
```

### Level 5: Autonomous Behaviors

```python
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.lidar = RPLidarC1()

@robot.loop(rate=10)  # 10 Hz
def navigate(state):
    if state.lidar.front < 30:
        robot.drive.rotate(0.5)  # Turn
    else:
        robot.drive.forward(0.3)

robot.start()  # Runs autonomously!
```

## Hardware

### Motors
- 4x MKS Servo42D (CAN bus)
- CAN IDs: 1-4 for wheels, 5 for gripper
- 80mm diameter mecanum wheels

### Sensors
- **Lidar**: RPLidar C1M1-R2 (360°, 12m range)
- **Camera**: Orbbec 3D (RGB + Depth)

### Interface
- CAN bus at 500kbps
- USB for sensors

## Project Structure

```
evabot/
├── evabot/              # Main library
│   ├── robot.py         # Robot container
│   ├── state.py         # Shared state
│   ├── components/      # Hardware components
│   │   ├── motor.py
│   │   ├── drives/
│   │   ├── sensors/
│   │   └── actuators/
│   ├── behaviors/       # High-level behaviors
│   └── slam/            # Mapping/localization
├── examples/            # Learning examples
└── tests/               # Unit tests
```

## Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed development roadmap
- [API Documentation](docs/api.md) - Complete API reference
- [Hardware Setup](docs/hardware_setup.md) - How to set up your robot
- [Tutorial](docs/tutorial.md) - Step-by-step learning path

## Development Status

### ✅ Completed
- Project structure
- Base classes

### 🚧 In Progress
- Motor component
- MecanumDrive

### 📋 Planned
- Sensors (Lidar, Camera)
- Autonomous behaviors
- SLAM

## Contributing

This is an educational project. Contributions welcome!

## License

MIT License - See LICENSE file for details

## Credits

Created for Eva and kids learning robotics 🎓
