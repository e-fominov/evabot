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

**Step 1: Install EvaBot on your computer**
```bash
git clone https://github.com/e-fominov/evabot.git
cd evabot
pip install -e .
```

**Step 2: Configure robot connection**
```bash
robot setup  # Interactive setup - enter your robot's IP/hostname
```

**Step 3: Install on robot (Raspberry Pi)**
```bash
robot install  # Copies package and sets up robot automatically
```

### Learning Workflow

**Create a lesson workspace anywhere:**
```bash
cd ~/my_robot_projects    # Any directory you want
robot lesson 1.2          # Creates lesson1_2/ with README & template
cd lesson1_2
cat README.md             # Read instructions
nano template.py          # Write your code
robot run template.py     # Run on physical robot!
```

**Get stuck? Include the solution:**
```bash
robot lesson 1.5 --solution  # Includes solution.py for reference
```

See [REMOTE_DEVELOPMENT.md](REMOTE_DEVELOPMENT.md) for advanced remote development features.

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

## Running on Your Robot

Run lessons and scripts on your physical robot:

```bash
# Create and run a lesson
robot lesson 1.2
cd lesson1_2
robot run template.py  # Runs on robot, output streams in real-time

# Run integration tests
robot run tests/integration/test_single_motor.py

# Run any script
robot run my_robot_program.py
```

All output streams to your terminal in real-time. See [REMOTE_DEVELOPMENT.md](REMOTE_DEVELOPMENT.md) for advanced features.

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

- [Learning Plan](LEARNING_PLAN.md) - Complete curriculum from beginner to maze solving
- [Remote Development](REMOTE_DEVELOPMENT.md) - Run code on your robot remotely
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed development roadmap
- [Architecture](ARCHITECTURE_V2.md) - System design and components
- [Lessons](lessons/) - Step-by-step tutorials for students

## Development Status

### ✅ Completed (Phase 1)
- ✅ Motor control (Servo42D with CAN bus)
- ✅ Position control (move by distance, move to position)
- ✅ Speed control (continuous running)
- ✅ Multi-motor coordination (4 motors tested)
- ✅ Integration tests (single + four motor suites)
- ✅ Educational lessons (Levels 1-3)
- ✅ Remote development tools

### 🚧 In Progress (Phase 2)
- MecanumDrive system
- Odometry tracking
- Drive patterns and movements

### 📋 Planned (Phase 3+)
- Sensors (RPLidar C1, Orbbec Camera)
- Autonomous behaviors and state machines
- SLAM and mapping
- Navigation and path planning

## Contributing

This is an educational project. Contributions welcome!

## License

MIT License - See LICENSE file for details

## Credits

Created for Eva and kids learning robotics 🎓
