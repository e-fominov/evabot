# EvaBot Learning Plan
**For kids 10+ (talented) / 12+ years old**

From "turn a motor" to "autonomous maze exploration"

---

## Level 1: Single Motor (1-2 hours)

### Lesson 1.1: Make It Spin
**Learn**: Connect to motor, make it turn
**Hardware**: 1 motor
**Code**: 5-10 lines
```python
from evabot import Motor
motor = Motor(1)
motor.run(30)
```

### Lesson 1.2: Control Speed
**Learn**: Change speed, reverse direction
**Hardware**: 1 motor
**Code**: 10-15 lines

### Lesson 1.3: Start and Stop
**Learn**: Hold, disable, stop methods
**Hardware**: 1 motor
**Code**: 10-15 lines

### Lesson 1.4: Read Position
**Learn**: Encoders, measure distance traveled
**Hardware**: 1 motor (with wheel)
**Code**: 15-20 lines

### Lesson 1.5: Move Exact Distance
**Learn**: Position control, move by degrees/rotations
**Hardware**: 1 motor
**Code**: 20-30 lines
```python
motor.zero_position()           # Set current as zero
motor.move_by(90, 40, 'degrees')  # Move 90 degrees
motor.move_to(0, 30, 'degrees')   # Return to zero
```

---

## Level 2: Multiple Motors (2-3 hours)

### Lesson 2.1: Two Motors Together
**Learn**: Control multiple motors, lists
**Hardware**: 2 motors
**Code**: 15-20 lines

### Lesson 2.2: Four Motors
**Learn**: All 4 motors, same/different speeds
**Hardware**: 4 motors
**Code**: 20-30 lines

### Lesson 2.3: Motor Patterns
**Learn**: Timing, sequences, for loops
**Hardware**: 4 motors
**Code**: 30-40 lines

---

## Level 3: Mecanum Drive (3-4 hours)

### Lesson 3.1: Forward and Backward
**Learn**: Use Drive system, basic movement
**Hardware**: 4 motors + mecanum wheels
**Code**: 10-15 lines
```python
from evabot import Robot, MecanumDrive
robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.drive.forward(0.3)
```

### Lesson 3.2: Strafe (Sideways)
**Learn**: Omnidirectional movement, mecanum magic
**Hardware**: Mecanum robot
**Code**: 15-20 lines

### Lesson 3.3: Rotation
**Learn**: Spin in place, turning
**Hardware**: Mecanum robot
**Code**: 15-20 lines

### Lesson 3.4: Combine Movements
**Learn**: Drive in any direction (vx, vy, rotation)
**Hardware**: Mecanum robot
**Code**: 20-30 lines

### Lesson 3.5: Drive a Square
**Learn**: Move exact distances, closed-loop control
**Hardware**: Mecanum robot
**Code**: 10-15 lines
```python
for i in range(4):
    robot.drive.move_forward(50)  # 50 cm
    robot.drive.turn_right(90)    # 90 degrees
```

### Lesson 3.6: Track Position
**Learn**: Odometry, where is the robot
**Hardware**: Mecanum robot
**Code**: 20-30 lines

---

## Level 4: Lidar Sensor (3-4 hours)

### Lesson 4.1: See Distances
**Learn**: Read lidar, measure to walls
**Hardware**: Robot + Lidar
**Code**: 10-15 lines
```python
robot.lidar = RPLidarC1()
robot.start()
print(robot.lidar.front)  # Distance in cm
```

### Lesson 4.2: Four Directions
**Learn**: Front, back, left, right
**Hardware**: Robot + Lidar
**Code**: 15-20 lines

### Lesson 4.3: Don't Hit Walls
**Learn**: If-statements, obstacle detection
**Hardware**: Robot + Lidar
**Code**: 20-30 lines
```python
if robot.lidar.front < 30:
    robot.drive.stop()
```

### Lesson 4.4: Simple Avoidance
**Learn**: Turn away from obstacles
**Hardware**: Robot + Lidar
**Code**: 30-40 lines

### Lesson 4.5: Wall Following
**Learn**: Keep distance to wall, drive parallel
**Hardware**: Robot + Lidar
**Code**: 40-50 lines

---

## Level 5: Camera Vision (3-4 hours)

### Lesson 5.1: See Colors
**Learn**: Camera, RGB image, color detection
**Hardware**: Robot + Camera
**Code**: 15-20 lines
```python
robot.camera = OrbbecCamera()
robot.start()
if robot.camera.red_detected:
    print("I see red!")
```

### Lesson 5.2: Find Objects
**Learn**: Locate colored objects (x, y position)
**Hardware**: Robot + Camera
**Code**: 20-30 lines

### Lesson 5.3: Measure Distance
**Learn**: Depth camera, how far is object
**Hardware**: Robot + Camera
**Code**: 20-30 lines

### Lesson 5.4: Track Object
**Learn**: Move toward/follow colored ball
**Hardware**: Robot + Camera
**Code**: 40-50 lines

### Lesson 5.5: Pick Up Object (Optional)
**Learn**: Gripper control, visual servoing
**Hardware**: Robot + Camera + Gripper
**Code**: 50-60 lines

---

## Level 6: Behavior Loops (2-3 hours)

### Lesson 6.1: Control Loop
**Learn**: @robot.loop decorator, repeated actions
**Hardware**: Robot (any sensors)
**Code**: 20-30 lines
```python
@robot.loop(rate=10)  # 10 times per second
def my_behavior(state):
    # Your code here
    pass
```

### Lesson 6.2: State Machine
**Learn**: Different modes, switching behaviors
**Hardware**: Robot + Lidar
**Code**: 40-50 lines

### Lesson 6.3: Wandering Robot
**Learn**: Explore randomly, avoid obstacles
**Hardware**: Robot + Lidar
**Code**: 40-60 lines

---

## Level 7: Combined Sensors (4-5 hours)

### Lesson 7.1: Lidar + Camera
**Learn**: Use both sensors together
**Hardware**: Robot + Lidar + Camera
**Code**: 40-50 lines

### Lesson 7.2: Find and Approach
**Learn**: Use lidar to navigate, camera to find target
**Hardware**: Robot + Lidar + Camera
**Code**: 50-70 lines

### Lesson 7.3: Safe Navigation
**Learn**: Camera sees goal, lidar avoids obstacles
**Hardware**: Robot + Lidar + Camera
**Code**: 60-80 lines

---

## Level 8: Mapping (4-6 hours)

### Lesson 8.1: Draw a Map
**Learn**: Create 2D grid map from lidar
**Hardware**: Robot + Lidar
**Code**: 30-40 lines (library does the work)
```python
robot.mapper = GridMapper()
robot.start_mapping()
# Drive around, map builds automatically
map = robot.mapper.get_map()  # 2D grid
robot.mapper.save_map("room.png")
```

### Lesson 8.2: Where Am I?
**Learn**: Localization on map
**Hardware**: Robot + Lidar
**Code**: 20-30 lines

### Lesson 8.3: Explore Mode
**Learn**: Automatic exploration, fill in map
**Hardware**: Robot + Lidar
**Code**: 30-40 lines

### Lesson 8.4: View the Map
**Learn**: Visualize map, see robot position
**Hardware**: Robot + Lidar
**Code**: 10-20 lines

---

## Level 9: Navigation (4-6 hours)

### Lesson 9.1: Go To Point
**Learn**: Navigate to (x, y) coordinate
**Hardware**: Robot + Lidar (with map)
**Code**: 15-25 lines
```python
robot.navigate_to(x=100, y=50)  # Go to (100, 50) cm
```

### Lesson 9.2: Waypoints
**Learn**: Visit multiple points in order
**Hardware**: Robot + Lidar (with map)
**Code**: 20-30 lines

### Lesson 9.3: Avoid Dynamic Obstacles
**Learn**: Path planning, replan when blocked
**Hardware**: Robot + Lidar (with map)
**Code**: 30-40 lines

### Lesson 9.4: Return Home
**Learn**: Remember start position, navigate back
**Hardware**: Robot + Lidar
**Code**: 20-30 lines

---

## Level 10: Maze Solving (5-8 hours)

### Lesson 10.1: Wall Following Strategy
**Learn**: Right-hand rule, simple maze solving
**Hardware**: Robot + Lidar
**Code**: 40-60 lines

### Lesson 10.2: Dead End Detection
**Learn**: Recognize dead ends, backtrack
**Hardware**: Robot + Lidar
**Code**: 50-70 lines

### Lesson 10.3: Map the Maze
**Learn**: Build maze map while exploring
**Hardware**: Robot + Lidar
**Code**: 40-60 lines (uses Level 8 mapping)

### Lesson 10.4: Find the Exit
**Learn**: Search algorithms, shortest path
**Hardware**: Robot + Lidar
**Code**: 60-80 lines
```python
# Library provides search, kid uses it
path = robot.mapper.find_path(start, goal)
robot.follow_path(path)
```

### Lesson 10.5: Solve Any Maze
**Learn**: Complete autonomous maze solver
**Hardware**: Robot + Lidar
**Code**: 80-100 lines

### Lesson 10.6: Race Mode
**Learn**: Optimize path, speed run
**Hardware**: Robot + Lidar
**Code**: 60-80 lines

---

## Projects (Self-Directed)

After completing all lessons, kids can build:

### Project Ideas:
- **Delivery Robot**: Navigate to colored markers
- **Security Patrol**: Follow route, report obstacles
- **Treasure Hunt**: Find colored objects in maze
- **Dance Routine**: Choreograph movement patterns
- **Line Follower**: Use camera to follow tape line
- **Sumo Robot**: Push opponent out of ring
- **Object Sorter**: Find and group by color
- **Remote Control**: Keyboard/gamepad control
- **Autonomy Challenge**: Complete course without help
- **Multi-Robot**: Coordinate 2+ robots (advanced)

---

## Skills Learned

### Programming:
- [ ] Variables and data types
- [ ] Functions and parameters
- [ ] If-statements (conditionals)
- [ ] Loops (for, while)
- [ ] Lists and dictionaries
- [ ] Decorators (@robot.loop)
- [ ] State machines
- [ ] Basic algorithms

### Robotics:
- [ ] Motor control
- [ ] Encoders and odometry
- [ ] Mecanum wheel kinematics
- [ ] Sensor reading
- [ ] Sensor fusion (combining data)
- [ ] Coordinate systems
- [ ] Path planning
- [ ] Mapping and localization
- [ ] Control loops
- [ ] PID control (hidden in library)

### Problem Solving:
- [ ] Break big problems into steps
- [ ] Debug when things don't work
- [ ] Test and iterate
- [ ] Parameter tuning
- [ ] Logical thinking
- [ ] Pattern recognition

---

## Time Estimates

**Fast learner (10-12 talented)**: 30-40 hours total
**Average learner (12+)**: 40-60 hours total
**Slower pace**: 60-80 hours total

**Recommended schedule**:
- 2-3 hours per week = 20-30 weeks (school year)
- 1 hour per day = 2-3 months (summer)
- Weekend projects = 10-15 weekends

---

## Prerequisites

**Before starting**:
- [ ] Basic Python syntax (variables, print, if/for)
- [ ] Can run Python programs
- [ ] Comfortable with terminal/command line
- [ ] Basic math (geometry helpful)
- [ ] Can solder wires (for hardware assembly)
- [ ] Adult supervision for power tools

**Not required**:
- ❌ Advanced math (calculus, linear algebra)
- ❌ ROS/ROS2 knowledge
- ❌ Computer vision algorithms
- ❌ SLAM algorithms
- ❌ Control theory
- ❌ C++ programming

All complex stuff is in the library!

---

## Assessment / Progress Tracking

### Can the student...

**Level 1-2**: ✓ Control motors independently
**Level 3**: ✓ Drive robot in all directions
**Level 4**: ✓ Avoid obstacles automatically
**Level 5**: ✓ Find and track colored objects
**Level 6**: ✓ Write behavior loops
**Level 7**: ✓ Combine multiple sensors
**Level 8**: ✓ Build a map of environment
**Level 9**: ✓ Navigate to target locations
**Level 10**: ✓ Solve mazes autonomously

**Mastery**: Student can design and implement their own robot behaviors for new challenges!

---

## Support Materials (To Be Created)

For each lesson:
- [ ] Step-by-step tutorial (with screenshots)
- [ ] Complete example code
- [ ] Video demonstration
- [ ] Common mistakes / troubleshooting
- [ ] Challenge exercises
- [ ] Quiz / self-assessment

---

## Parent/Teacher Guide

**How to help**:
- Let them struggle a bit (builds problem-solving)
- Encourage experimentation
- Celebrate small wins
- Help debug when truly stuck
- Provide safe space for hardware work
- Don't solve problems for them

**When to step in**:
- Safety issues (electrical, mechanical)
- Hardware malfunction (broken sensor)
- Completely stuck for 30+ minutes
- Frustration level too high

**Progress indicators**:
- Can explain what their code does
- Asks good debugging questions
- Tries multiple approaches
- Excited to show you what they built
- Wants to add new features

---

**Ready to build!** 🤖
