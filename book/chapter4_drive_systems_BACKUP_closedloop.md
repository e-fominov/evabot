# Chapter 4: Drive Systems & Closed-Loop Control

**Learn how robots move and know where they are**

In the previous chapters, you learned to control individual motors and make them work together. Now you'll learn how to make your robot move like a real mobile robot - with intelligent control systems that know exactly where the robot is and where it's going.

---

## Table of Contents

1. [Theory: Types of Drive Systems](#theory-types-of-drive-systems)
2. [Coordinate Systems & Directions](#coordinate-systems--directions)
3. [Open-Loop vs Closed-Loop Control](#open-loop-vs-closed-loop-control)
4. [What is Odometry?](#what-is-odometry)
5. [Units & Conversions](#units--conversions)
6. [Understanding Your Mecanum Robot](#understanding-your-mecanum-robot)
7. [Building Your Drive System](#building-your-drive-system)
8. [Closed-Loop Movements](#closed-loop-movements)
9. [Calibration: Making it Accurate](#calibration-making-it-accurate)
10. [Understanding Errors & Drift](#understanding-errors--drift)
11. [Safety & Best Practices](#safety--best-practices)

---

## Theory: Types of Drive Systems

Different robots use different drive systems. Let's understand the main types:

### 1. Differential Drive (Tank Drive)
```
    FRONT
   ┌─────┐
 ●─┤     ├─●  ← Two wheels (left & right)
   │     │
   └─────┘
    BACK
```

**How it works:**
- Two powered wheels (left & right)
- Often has caster wheels for balance
- Examples: Mars rovers, Roomba, most beginner robots

**What it can do:**
- ✅ Move forward/backward (both wheels same speed, same direction)
- ✅ Rotate in place (wheels same speed, opposite directions)
- ✅ Drive in arcs (wheels different speeds)
- ❌ Cannot strafe sideways

**Control:** Only 2 values needed: `left_speed`, `right_speed`

---

### 2. Mecanum Drive (Your Robot!)
```
    FRONT
  FL ╱╲ FR     ← 4 wheels with angled rollers
    ╱  ╲
   ╱    ╲
  BL ╲╱ BR
    BACK
```

**How it works:**
- Four wheels with angled rollers (45° to wheel axis)
- Rollers allow sideways sliding
- By controlling all 4 wheels, you can move in ANY direction!

**What it can do:**
- ✅ Move forward/backward
- ✅ Strafe left/right (sideways!)
- ✅ Rotate in place
- ✅ Move diagonally
- ✅ **Do all three at once!** (forward + sideways + rotating)

**Control:** 3 values needed: `vx` (forward), `vy` (sideways), `vtheta` (rotation)

This is called **omnidirectional movement** - you can move in any direction without turning first!

---

### 3. Other Drive Types (For Reference)

**Ackermann Steering** (Car-like):
```
    ┌─────┐
    │ ╱ ╲ │  ← Front wheels steer
  ●─┤     ├─●
    └─────┘
```
- Like a car - front wheels steer, rear wheels drive
- Can't rotate in place or strafe
- Good for high speeds

**Omni-Wheel Drive**:
```
  Similar to mecanum, but rollers perpendicular to wheel
```
- Like mecanum, but different wheel design
- Also omnidirectional

---

## Coordinate Systems & Directions

This is **super important** for understanding how robots move!

### The Two Coordinate Systems

#### 1. Robot Frame (Body Frame)
The robot's own perspective:
```
        ^ X (forward)
        |
    FL  |  FR
      \ | /
       \|/
  Y <---●      ← Robot center
       /|\
      / | \
    BL  |  BR
        |

X = forward/backward
Y = left/right
Theta = rotation angle
```

**From the robot's view:**
- `vx > 0`: "I'm moving forward"
- `vy > 0`: "I'm moving left"
- `vtheta > 0`: "I'm rotating counter-clockwise"

These directions are **always the same** for the robot, no matter which way it faces!

---

#### 2. World Frame (Global Frame)
The room's perspective (fixed in space):
```
        ^ Y (North)
        |
        |
        |
  X <---●  (0, 0)
      (Origin)

X = East/West
Y = North/South
```

This frame doesn't move - it's fixed to the room/floor.

---

### Why Two Frames?

**Example:** Your robot starts at `(0, 0)` facing North:

1. You tell it: `move(vx=1.0)` - move forward 1 m/s
   - **Robot thinks:** "I'm going forward" (robot frame)
   - **World sees:** "It's going North" (world frame: Y increases)

2. Robot rotates to face East, you say: `move(vx=1.0)` again
   - **Robot thinks:** "I'm going forward" (still vx!)
   - **World sees:** "Now it's going East" (world frame: X increases)

**Key insight:**
- You **command** in robot frame (vx, vy, vtheta)
- Odometry **tracks** in world frame (x, y, theta)

---

### Exercise 4.1: Coordinate Transform 🧮

**Question 1:** Robot is at position `(0, 0)` facing East (θ = 0°). It moves forward 2 meters. What is its new world position?

<details>
<summary>Click for answer</summary>

Since robot faces East (positive X direction):
- Forward motion (vx) → X increases
- New position: `(2, 0)`

</details>

---

**Question 2:** Robot is at `(3, 0)` facing North (θ = 90°). It moves forward 4 meters. What is its new world position?

<details>
<summary>Click for answer</summary>

Robot faces North (positive Y direction):
- Forward motion (vx) → Y increases
- New position: `(3, 4)`

</details>

---

**Question 3:** Robot is at `(0, 0)` facing Northeast (θ = 45°). It moves forward 10 meters. What is its new world position?

*Hint: Use sin and cos! At 45°, both sin(45°) = cos(45°) = 0.707*

<details>
<summary>Click for answer</summary>

```python
import math
theta = math.radians(45)  # Convert to radians
distance = 10

dx = distance * math.cos(theta) = 10 * 0.707 = 7.07 m
dy = distance * math.sin(theta) = 10 * 0.707 = 7.07 m

New position: (7.07, 7.07)
```

</details>

---

### Exercise 4.2: Distance and Angle 🧮

**Question 1:** Robot is at position `(3, 4)`. How far is it from the origin `(0, 0)`?

*Hint: Pythagorean theorem! distance = √(x² + y²)*

<details>
<summary>Click for answer</summary>

```python
import math
distance = math.sqrt(3**2 + 4**2)
distance = math.sqrt(9 + 16)
distance = math.sqrt(25) = 5 meters
```

</details>

---

**Question 2:** Robot is at position `(3, 4)`. What angle does it make with the X-axis?

*Hint: Use atan2! angle = atan2(y, x)*

<details>
<summary>Click for answer</summary>

```python
import math
angle_rad = math.atan2(4, 3) = 0.927 radians
angle_deg = math.degrees(0.927) = 53.1 degrees
```

</details>

---

**Question 3:** Robot wants to move from `(0, 0)` to `(5, 5)`. What direction (angle) should it face?

<details>
<summary>Click for answer</summary>

```python
import math
dx = 5 - 0 = 5
dy = 5 - 0 = 5
angle = math.atan2(dy, dx) = math.atan2(5, 5)
angle = 0.785 radians = 45 degrees (Northeast!)
```

</details>

---

## Open-Loop vs Closed-Loop Control

Two fundamental ways to control a robot:

### Open-Loop Control

**Concept:** Give a command, hope for the best, don't check results.

**Example:**
```python
# "Run motors for 3 seconds, hope we go 30cm"
robot.drive.forward(0.1)  # 0.1 m/s
time.sleep(3.0)
robot.drive.halt()
# Did we go 30cm? Who knows! 🤷
```

**Pros:**
- ✅ Simple to program
- ✅ Fast (no sensor reading)
- ✅ Works if conditions are perfect

**Cons:**
- ❌ No idea where you actually are
- ❌ Errors accumulate (floor slippery? battery low?)
- ❌ Can't correct mistakes

**When to use:** Quick movements, don't care about precision

---

### Closed-Loop Control

**Concept:** Measure where you are, compare to where you want to be, adjust.

**Example:**
```python
# "I want to go exactly 0.5 meters forward"
start_x = robot.odom.pose.x

while True:
    current_x = robot.odom.pose.x
    distance_traveled = current_x - start_x

    if distance_traveled >= 0.5:
        robot.drive.halt()
        break

    # Keep going
    robot.drive.forward(0.1)
    time.sleep(0.01)

# We went 0.5m (with small error)! ✓
```

**Pros:**
- ✅ Accurate (corrects for errors)
- ✅ Knows current position
- ✅ Can detect problems (stuck? slipping?)

**Cons:**
- ❌ Needs sensors (encoders)
- ❌ More complex code
- ❌ Slight delay from sensing

**When to use:** Precise movements, navigation, autonomy

---

### The Feedback Loop

Closed-loop control uses a feedback loop:

```
┌──────────────────────────────────────┐
│                                      │
│  Goal ──> Controller ──> Motors ──> Position
│            ^                          │
│            │                          │
│            └────── Sensors ───────────┘
│                   (Encoders)
└──────────────────────────────────────┘
```

1. **Goal:** "Go to x=1.0 meters"
2. **Sensors:** "Currently at x=0.3 meters"
3. **Controller:** "Need 0.7m more, keep moving"
4. **Motors:** Move forward
5. **Repeat** until goal reached!

This is also called **feedback control** or **PID control** (Proportional-Integral-Derivative).

Your `MecanumDrive` uses closed-loop control with **odometry** (measuring position from wheel encoders).

---

## What is Odometry?

**Odometry** = measuring distance traveled using wheel encoders.

### How It Works

1. **Encoders count wheel rotations** (in pulses)
   - Your Servo42D motors: 3200 pulses per revolution

2. **Convert pulses to distance**
   ```python
   rotations = pulses / 3200
   distance = rotations × (2 × π × wheel_radius)
   ```

3. **Combine all 4 wheels to get robot motion**
   - Forward/backward: all wheels same direction
   - Strafe: wheels opposite patterns
   - Rotation: wheels create spin

4. **Integrate motion over time** → position (x, y, theta)

---

### The Odometry Update Loop

Your robot runs this in the background (50 times per second!):

```python
# Simplified version of what happens
while robot_running:
    # 1. Read all encoder positions
    fl_pulses = motor_fl.get_position()
    fr_pulses = motor_fr.get_position()
    # ... (bl, br)

    # 2. Calculate how much each wheel moved
    delta_fl = fl_pulses - last_fl_pulses
    # Convert to meters
    distance_fl = delta_fl * (2*pi*radius) / 3200

    # 3. Use mecanum kinematics to get robot motion
    dx = ...  # Robot moved this far forward
    dy = ...  # Robot moved this far left
    dtheta = ...  # Robot rotated this much

    # 4. Update position in world frame
    x = x + dx*cos(theta) - dy*sin(theta)
    y = y + dx*sin(theta) + dy*cos(theta)
    theta = theta + dtheta

    # 5. Save for next iteration
    last_fl_pulses = fl_pulses

    time.sleep(0.02)  # 50 Hz
```

You can access the result anytime:
```python
print(robot.odom.pose.x)      # meters
print(robot.odom.pose.y)      # meters
print(robot.odom.pose.theta)  # radians
```

---

### Odometry is Not Perfect!

Odometry **drifts** over time because:
- ❌ Wheels slip on smooth floors
- ❌ Wheel diameter not exactly 50mm (manufacturing tolerance)
- ❌ Wheelbase/track_width measurements slightly off
- ❌ Encoder resolution limited (3200 pulses = ~0.1mm per pulse)

**Result:** After driving 10 meters, you might be off by 5-10 cm.

**Solution:** Use additional sensors (lidar, camera) to correct odometry. This is called **sensor fusion** - coming in later chapters!

---

## Units & Conversions

Robotics uses different units. You need to convert between them!

### Distance

- **Meters (m)**: Standard in robotics
  - Example: `0.5 m` = 50 cm

- **Centimeters (cm)**: Easier for small robots
  - Example: `50 cm` = 0.5 m

**Conversion:**
```python
meters = centimeters / 100
centimeters = meters * 100
```

---

### Velocity (Speed)

- **Meters per second (m/s)**: Standard
  - Example: `0.3 m/s` = 30 cm/s

- **Centimeters per second (cm/s)**: Sometimes easier to think about

**Conversion:**
```python
m_per_s = cm_per_s / 100
cm_per_s = m_per_s * 100
```

---

### Angle

- **Radians (rad)**: Standard in programming (sin, cos, atan2)
  - Full circle = `2π` radians ≈ 6.28 radians
  - Right angle = `π/2` radians ≈ 1.57 radians

- **Degrees (°)**: Easier for humans
  - Full circle = 360°
  - Right angle = 90°

**Conversion:**
```python
import math

radians = math.radians(degrees)  # degrees → radians
degrees = math.degrees(radians)  # radians → degrees

# Manual:
radians = degrees * (math.pi / 180)
degrees = radians * (180 / math.pi)
```

---

### Angular Velocity (Rotation Speed)

- **Radians per second (rad/s)**: Standard
  - Example: `0.5 rad/s` ≈ 28.6°/s

- **Degrees per second (°/s)**: Sometimes clearer
  - Example: `90°/s` ≈ 1.57 rad/s

- **RPM (Revolutions Per Minute)**: Motors often specified this way
  - 1 revolution = 2π radians
  - 1 RPM = (2π / 60) rad/s ≈ 0.105 rad/s

---

### Exercise 4.3: Unit Conversions 🧮

**Question 1:** Convert 45 cm to meters.

<details>
<summary>Answer</summary>

```python
meters = 45 / 100 = 0.45 m
```
</details>

---

**Question 2:** Convert 0.25 m/s to cm/s.

<details>
<summary>Answer</summary>

```python
cm_per_s = 0.25 * 100 = 25 cm/s
```
</details>

---

**Question 3:** Convert 180° to radians.

<details>
<summary>Answer</summary>

```python
import math
radians = math.radians(180) = 3.14159... (π radians)
```
</details>

---

**Question 4:** Convert 1.0 rad/s to degrees per second.

<details>
<summary>Answer</summary>

```python
import math
degrees_per_s = math.degrees(1.0) = 57.3°/s
```
</details>

---

**Question 5:** A wheel rotates at 30 RPM. What is the angular velocity in rad/s?

<details>
<summary>Answer</summary>

```python
import math
rad_per_s = 30 * (2 * math.pi / 60)
rad_per_s = 30 * 0.105 = 3.14 rad/s
```
</details>

---

## Understanding Your Mecanum Robot

Before programming, you need to understand your robot's physical setup.

### Mecanum Wheel Patterns

There are **two** common mecanum patterns. Your robot uses the **X pattern**.

#### X Pattern (Most Common)
```
    FRONT
  FL ╲ ╱ FR     FL: \ rollers (forward-left)
      X         FR: / rollers (forward-right)
  BL ╱ ╲ BR     BL: / rollers (forward-right)
                BR: \ rollers (forward-left)
    BACK
```

Top view of rollers forms an "X" shape.

---

#### Diamond Pattern (Alternative)
```
    FRONT
  FL ╱ ╲ FR     FL: / rollers
      ╳         FR: \ rollers
  BL ╲ ╱ BR     BL: \ rollers
                BR: / rollers
    BACK
```

Top view of rollers forms a diamond shape.

**How to tell which you have:**
1. Look at front-left wheel from above
2. Does the roller contact point lean forward-left (\) or forward-right (/)?
   - Forward-left (\) → X pattern
   - Forward-right (/) → Diamond pattern

---

### Identifying Your Motors

You need to know which motor is which! Here's how:

#### Method 1: Physical Labels
Check if motors have labels or colored wires:
- Motor 1, 2, 3, 4?
- Different colored wire wraps?

#### Method 2: Test One at a Time
```python
from evabot import Robot
from evabot.components.motors import Servo42D

# Test motor with CAN ID 1
motor = Servo42D(1)
motor.start()
motor.run(20)  # Slow speed

# Watch which wheel spins!
# Mark it with tape

time.sleep(3)
motor.stop()
```

Repeat for IDs 2, 3, 4. Mark each wheel with tape!

#### Method 3: Check Existing Code
If you've used lessons already:
```python
# From lesson 2.2 or 3.1
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
#                          ↑   ↑   ↑   ↑
#                         These are your motor IDs!
```

---

### Physical Measurements

For accurate odometry, you need to measure your robot:

#### 1. Wheel Radius
```
    ___
   /   \
  |  r  |  ← Measure diameter, divide by 2
   \___/

diameter = ?? mm
radius = diameter / 2 / 1000  (convert to meters)
```

**How to measure:**
- Use ruler or calipers
- Measure across the wheel (diameter)
- Include the roller thickness!
- Default: 50mm radius (100mm diameter)

---

#### 2. Wheelbase (Front-to-Back)
```
  FL ●─┐
       │ ← wheelbase
  BL ●─┘

Distance from front axle to back axle
```

**How to measure:**
- Measure center of front wheel to center of back wheel
- Default: 200mm (0.20 m)

---

#### 3. Track Width (Left-to-Right)
```
  FL ●────● FR
      ↑
   track_width

Distance from left wheels to right wheels
```

**How to measure:**
- Measure center of left wheel to center of right wheel
- Default: 200mm (0.20 m)

---

### Exercise 4.4: Measure Your Robot 📏

Grab a ruler and measure:

1. **Wheel diameter:** _____ mm
   - Wheel radius = _____ mm = _____ m

2. **Wheelbase (front-to-back):** _____ mm = _____ m

3. **Track width (left-to-right):** _____ mm = _____ m

Write these down! You'll use them when creating your drive system.

---

### Troubleshooting Motor Directions

When you first test your robot, it might not move correctly. Here's how to fix it:

#### Problem 1: Robot Goes Backward When You Say Forward

**Cause:** All motors spinning wrong direction

**Fix:** Invert all motor directions in code, or physically swap motor wiring

---

#### Problem 2: Robot Spins When You Say Go Straight

**Cause:** One or more motors spinning wrong direction

**Fix:** Test each motor individually. Find the one(s) going backward. Either:
- Swap that motor's wiring
- Invert it in code (negative speed)

---

#### Problem 3: Robot Goes Diagonal Instead of Straight

**Cause:** Motors not matched to correct positions (FL, FR, BL, BR mixed up)

**Fix:**
1. Test each motor individually
2. Mark which physical wheel is which CAN ID
3. Update your `MecanumDrive(fl=?, fr=?, bl=?, br=?)` with correct IDs

---

## Building Your Drive System

Now let's create a `MecanumDrive` object!

### Basic Setup

```python
from evabot import Robot, MecanumDrive

# Create robot
robot = Robot()

# Create mecanum drive
robot.drive = MecanumDrive(
    fl=4,           # Front-left motor CAN ID
    fr=2,           # Front-right motor CAN ID
    bl=3,           # Back-left motor CAN ID
    br=1,           # Back-right motor CAN ID
    pattern='X'     # X pattern (most common)
)

# Start the robot (enables motors, starts odometry)
robot.start()

# Now you can drive!
robot.drive.forward(0.3)  # 0.3 m/s forward
```

---

### Full Configuration

If you measured your robot dimensions:

```python
robot.drive = MecanumDrive(
    fl=4, fr=2, bl=3, br=1,

    # Robot geometry (in meters!)
    wheel_radius=0.050,      # 50mm wheels
    wheel_base=0.200,        # 200mm front-to-back
    track_width=0.200,       # 200mm left-to-right

    # Encoder resolution
    pulses_per_rev=3200,     # Servo42D default

    # CAN bus settings
    channel='can0',
    bitrate=500000,

    # Wheel pattern
    pattern='X'              # or 'diamond'
)
```

---

### What Happens When You Call `robot.start()`?

1. **Enables all 4 motors** (connects to CAN bus)
2. **Starts odometry thread** (runs at 50 Hz in background)
3. **Initializes position** to (0, 0, 0)

From now on, `robot.odom.pose` always shows your position!

---

## Closed-Loop Movements

Now for the fun part - making your robot move with precision!

### The Three Velocities

Remember, mecanum drive uses **three independent velocities**:

```python
robot.drive.move(vx=?, vy=?, vtheta=?)
```

- `vx`: Forward/backward speed (m/s)
  - Positive = forward
  - Negative = backward

- `vy`: Left/right speed (m/s)
  - Positive = left (strafe left)
  - Negative = right (strafe right)

- `vtheta`: Rotation speed (rad/s)
  - Positive = counter-clockwise (CCW)
  - Negative = clockwise (CW)

**All three are independent!** You can combine them in any way.

---

### Basic Movements

#### Forward
```python
robot.drive.forward(0.3)  # 0.3 m/s forward

# Same as:
robot.drive.move(vx=0.3, vy=0, vtheta=0)
```

#### Backward
```python
robot.drive.backward(0.3)  # 0.3 m/s backward

# Same as:
robot.drive.move(vx=-0.3, vy=0, vtheta=0)
```

#### Strafe Left
```python
robot.drive.strafe_left(0.2)  # 0.2 m/s left

# Same as:
robot.drive.move(vx=0, vy=0.2, vtheta=0)
```

#### Strafe Right
```python
robot.drive.strafe_right(0.2)  # 0.2 m/s right

# Same as:
robot.drive.move(vx=0, vy=-0.2, vtheta=0)
```

#### Rotate Counter-Clockwise
```python
robot.drive.rotate_ccw(0.5)  # 0.5 rad/s CCW

# Same as:
robot.drive.move(vx=0, vy=0, vtheta=0.5)
```

#### Rotate Clockwise
```python
robot.drive.rotate_cw(0.5)  # 0.5 rad/s CW

# Same as:
robot.drive.move(vx=0, vy=0, vtheta=-0.5)
```

#### Stop
```python
robot.drive.halt()

# Same as:
robot.drive.move(vx=0, vy=0, vtheta=0)
```

---

### Combined Movements

This is where mecanum gets awesome!

#### Diagonal Movement
```python
# Forward and left at the same time
robot.drive.move(vx=0.3, vy=0.2, vtheta=0)
# Robot moves diagonally forward-left!
```

#### Driving in an Arc
```python
# Forward while rotating
robot.drive.move(vx=0.3, vy=0, vtheta=0.5)
# Robot drives forward in a curved path
```

#### The Full Power
```python
# Forward + left + rotating CCW, all at once!
robot.drive.move(vx=0.3, vy=0.1, vtheta=0.2)
# This is omnidirectional movement!
```

---

### Move by Distance (Closed-Loop!)

Here's where closed-loop control shines - move **exactly** a certain distance:

```python
import time

# Move forward exactly 0.5 meters
start_x = robot.odom.pose.x

robot.drive.forward(0.2)  # Start moving

while True:
    current_x = robot.odom.pose.x
    distance = current_x - start_x

    if distance >= 0.5:
        robot.drive.halt()
        break

    time.sleep(0.01)  # Check 100 times/second

print(f"Traveled {distance:.3f} meters")
```

**Try this!** It should go very close to 50 cm.

---

### Move by Time (Open-Loop... for now)

You can also move for a specific time:

```python
import time

# Move forward for 3 seconds
robot.drive.forward(0.2)
time.sleep(3.0)
robot.drive.halt()

# How far did we go?
# Speed × Time = 0.2 m/s × 3s = 0.6 meters (approximately)
# Check with odometry!
print(f"Position: {robot.odom.pose.x:.3f} m")
```

**Note:** This is technically open-loop (we're not using feedback to control distance), but we're using odometry to *measure* the result!

---

### Movement Patterns

Let's make interesting patterns:

#### Square Pattern
```python
import time

# Drive in a 0.5m × 0.5m square
for i in range(4):
    robot.drive.forward(0.2)
    time.sleep(2.5)  # 0.2 m/s × 2.5s = 0.5m
    robot.drive.halt()

    robot.drive.rotate_ccw(0.5)
    time.sleep(math.pi)  # 0.5 rad/s × π s = 90° turn
    robot.drive.halt()

    time.sleep(0.5)  # Pause

robot.drive.halt()
```

#### Figure-8 Pattern
```python
import time

# Drive in figure-8 (two circles)
for i in range(2):
    # Circle clockwise
    robot.drive.move(vx=0.2, vtheta=-0.4)
    time.sleep(15)  # Approximately one circle

    # Circle counter-clockwise
    robot.drive.move(vx=0.2, vtheta=0.4)
    time.sleep(15)

robot.drive.halt()
```

---

### Monitoring Position

While moving, you can always check where you are:

```python
robot.drive.forward(0.3)

for i in range(10):
    pose = robot.odom.pose
    print(f"x={pose.x:.3f}m, y={pose.y:.3f}m, θ={pose.theta:.3f}rad")
    time.sleep(0.5)

robot.drive.halt()
```

---

### Practice Lessons

Now try the actual lessons! They build on these concepts:

- **Lesson 3.1**: Forward and Backward
- **Lesson 3.2**: Strafe (Sideways)
- **Lesson 3.3**: Rotation
- **Lesson 3.4**: Combine Movements
- **Lesson 3.5**: Drive a Square
- **Lesson 3.6**: Track Position

Each lesson has:
- `template.py` - Fill in the blanks
- `solution.py` - Working code
- `README.md` - Detailed instructions

**Start with:** `robot lesson 3.1`

---

## Calibration: Making it Accurate

Your robot's odometry depends on accurate measurements. Let's calibrate!

### Why Calibrate?

Even small errors compound:
- Wheel radius off by 1mm → 2% distance error
- After 10 meters → 20cm error!

Let's fix that.

---

### Step 1: Calibrate Wheel Diameter

**Test:** Drive forward 1 meter, measure actual distance traveled.

```python
from evabot import Robot, MecanumDrive
import time

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.start()

time.sleep(1)

# Record start position
start_x = robot.odom.pose.x
print(f"Starting at x={start_x:.3f}m")

# Drive forward 1 meter (according to odometry)
robot.drive.forward(0.2)

while True:
    current_x = robot.odom.pose.x
    distance = current_x - start_x

    if distance >= 1.0:
        robot.drive.halt()
        break

    time.sleep(0.01)

print(f"Odometry says: {distance:.3f}m")
print("Now measure actual distance with a ruler!")

robot.stop()
```

**Instructions:**
1. Mark robot's starting position with tape
2. Run the program
3. Mark robot's ending position with tape
4. Measure the actual distance between marks with a ruler

**Results:**
- Odometry says: 1.000 m
- Ruler says: ??? m (measure this!)

---

### Step 2: Calculate Correction Factor

```python
measured_distance = 0.95  # What you measured (example)
commanded_distance = 1.0   # What we asked for

correction_factor = measured_distance / commanded_distance
# Example: 0.95 / 1.0 = 0.95

# This means wheels are slightly smaller than we thought
```

---

### Step 3: Update Wheel Radius

```python
old_radius = 0.050  # 50mm
new_radius = old_radius * correction_factor
# Example: 0.050 × 0.95 = 0.0475 m (47.5mm)

print(f"Update wheel_radius to: {new_radius:.4f}")
```

Now update your code:
```python
robot.drive = MecanumDrive(
    fl=4, fr=2, bl=3, br=1,
    wheel_radius=0.0475,  # ← Updated value!
)
```

---

### Step 4: Test Again

Run the 1-meter test again with new radius. It should be much more accurate!

**Tip:** You may need to iterate 2-3 times to get it perfect.

---

### Calibrating Rotation

Same idea for rotation:

```python
import math

# Rotate exactly 360° (2π radians)
start_theta = robot.odom.pose.theta

robot.drive.rotate_ccw(0.3)

while True:
    current_theta = robot.odom.pose.theta
    rotated = current_theta - start_theta

    if rotated >= 2 * math.pi:
        robot.drive.halt()
        break

    time.sleep(0.01)

print("Odometry says: 360° rotation")
print("Did the robot actually complete a full circle?")
# Mark starting orientation with tape, check if it returned!
```

If robot over/under-rotates, adjust `wheel_base` and `track_width` slightly.

---

## Understanding Errors & Drift

Even with perfect calibration, odometry drifts. Let's understand why.

### The Square Test

This is a classic test to see odometry error:

```python
import time
import math

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.start()

time.sleep(1)

# Record starting position
start_pose = robot.odom.pose
print(f"Start: x={start_pose.x:.3f}, y={start_pose.y:.3f}, θ={start_pose.theta:.3f}")

# Drive a 1m × 1m square
for i in range(4):
    print(f"\nSide {i+1}:")

    # Drive forward 1 meter
    start_x = robot.odom.pose.x
    start_y = robot.odom.pose.y

    robot.drive.forward(0.2)

    while True:
        dx = robot.odom.pose.x - start_x
        dy = robot.odom.pose.y - start_y
        dist = math.sqrt(dx**2 + dy**2)

        if dist >= 1.0:
            robot.drive.halt()
            break

        time.sleep(0.01)

    print(f"  After forward: x={robot.odom.pose.x:.3f}, y={robot.odom.pose.y:.3f}")
    time.sleep(0.5)

    # Rotate 90° left
    start_theta = robot.odom.pose.theta
    robot.drive.rotate_ccw(0.3)

    while True:
        rotated = robot.odom.pose.theta - start_theta

        if rotated >= math.pi / 2:  # 90°
            robot.drive.halt()
            break

        time.sleep(0.01)

    print(f"  After rotate: θ={robot.odom.pose.theta:.3f}rad ({math.degrees(robot.odom.pose.theta):.1f}°)")
    time.sleep(0.5)

# Check final position
end_pose = robot.odom.pose
print(f"\nEnd: x={end_pose.x:.3f}, y={end_pose.y:.3f}, θ={end_pose.theta:.3f}")

# Calculate error
error_x = end_pose.x - start_pose.x
error_y = end_pose.y - start_pose.y
error_theta = end_pose.theta - start_pose.theta

error_dist = math.sqrt(error_x**2 + error_y**2)

print(f"\nError: {error_dist*100:.1f}cm position, {math.degrees(error_theta):.1f}° orientation")

robot.stop()
```

**Expected Result:** Robot should return near start position, but won't be perfect!

Typical errors: 2-10 cm position, 2-5° orientation

---

### Sources of Error

#### 1. Wheel Slip
- Smooth floors (tile, polished concrete)
- Fast acceleration
- Sharp turns
**Solution:** Slower speeds, better floor (carpet, rubber mat)

#### 2. Measurement Errors
- Wheel diameter not exact (manufacturing tolerance)
- Wheel radius changes with tire wear
- Wheelbase/track_width not measured precisely
**Solution:** Careful calibration

#### 3. Encoder Resolution
- 3200 pulses/rev ≈ 0.1mm per pulse
- Small movements have quantization error
**Solution:** Can't fix (hardware limit), but 0.1mm is pretty good!

#### 4. Mechanical Issues
- Wheels not perfectly parallel
- Motors have slightly different speeds
- Flexibility in robot frame
**Solution:** Better mechanical design, tighter tolerances

#### 5. Computation Errors
- Odometry updates at 50 Hz (every 20ms)
- Between updates, motion assumed constant
- Fast movements or sudden stops → small errors
**Solution:** Higher update rate (but diminishing returns)

---

### Error Accumulation

Odometry errors **accumulate** over time:

```
After 1 meter:  ±1 cm error
After 10 meters: ±10 cm error
After 100 meters: ±1 meter error!
```

This is called **drift** - position estimate slowly drifts from true position.

**Why it happens:**
- Each time step has small error (e.g., 0.1% per meter)
- Errors add up: 100 meters × 0.1% = 10 cm error
- Errors in orientation cause even more position drift!

**Solution:**
- **Short term:** Odometry is great! (errors small)
- **Long term:** Need external references (lidar, camera, GPS)
- **Best:** Sensor fusion (combine odometry + sensors)

We'll learn sensor fusion in later chapters!

---

## Safety & Best Practices

### Speed Limits

Start slow, speed up as you gain confidence:

**Beginner speeds:**
```python
# Safe for learning
robot.drive.forward(0.1)      # 10 cm/s
robot.drive.rotate_ccw(0.2)   # 0.2 rad/s ≈ 11°/s
```

**Intermediate speeds:**
```python
# After some practice
robot.drive.forward(0.3)      # 30 cm/s
robot.drive.rotate_ccw(0.5)   # 0.5 rad/s ≈ 29°/s
```

**Advanced speeds:**
```python
# When you're confident
robot.drive.forward(0.5)      # 50 cm/s
robot.drive.rotate_ccw(1.0)   # 1 rad/s ≈ 57°/s
```

**WARNING:** Don't exceed these without testing:
```python
# FAST - be careful!
robot.drive.forward(1.0)      # 1 m/s = 100 cm/s
robot.drive.rotate_ccw(2.0)   # 2 rad/s ≈ 115°/s
```

---

### Emergency Stop

Always know how to stop!

**Method 1: In code**
```python
robot.drive.halt()  # Stop all motion
```

**Method 2: Keyboard**
Press `Ctrl+C` to kill the Python program:
```
^CKeyboardInterrupt
```

Your `robot.stop()` should be called automatically (if you used proper cleanup).

**Method 3: Power**
Physical emergency stop button (if your robot has one), or disconnect battery.

---

### Safe Testing

1. **Start on the floor** (not on a table!)
2. **Test in open space** (no obstacles nearby)
3. **Low speed first** (0.1-0.2 m/s)
4. **Hands ready** to catch/stop robot
5. **One feature at a time** (test forward, then strafe, then rotate...)

---

### What If Robot Acts Weird?

#### Robot vibrates/jitters but doesn't move
- **Cause:** Speed too low, motors fighting friction
- **Fix:** Increase speed to at least 0.05 m/s

#### Robot curves instead of going straight
- **Cause:** Motors not balanced, or one motor direction wrong
- **Fix:** Test each motor individually, check wiring

#### Robot goes opposite direction
- **Cause:** All motor directions inverted
- **Fix:** Swap motor wiring or negate speeds in code

#### Odometry way off
- **Cause:** Wrong wheel_radius, wheelbase, or track_width
- **Fix:** Measure carefully and calibrate

#### Robot doesn't respond
- **Cause:** CAN bus not working, motors not connected
- **Fix:** Check `robot.start()` output, verify CAN connection

---

## Summary

In this chapter you learned:

✅ **Theory:**
- Types of drive systems (differential, mecanum, ackermann)
- Coordinate systems (robot frame vs world frame)
- Open-loop vs closed-loop control
- What odometry is and how it works
- Unit conversions (m/s, rad/s, degrees)

✅ **Practice:**
- Identify your robot's motors and wheel pattern
- Measure robot dimensions
- Create a MecanumDrive object
- Move with closed-loop control (forward, strafe, rotate)
- Combine movements (omnidirectional!)
- Monitor position with odometry

✅ **Calibration:**
- Test actual vs commanded distance
- Calculate correction factors
- Update wheel_radius
- Square test for drift

✅ **Understanding:**
- Why odometry drifts
- Sources of error
- Error accumulation
- Limitations of wheel encoders

---

## What's Next?

**Chapter 5: Open-Loop Control** (Coming Soon)
- Time-based movement
- Velocity control without feedback
- When to use open-loop
- Combining open-loop and closed-loop

**After that:**
- **Chapter 6: Sensors** (Lidar & Camera)
- **Chapter 7: Autonomous Behaviors** (State machines, reactive control)
- **Chapter 8: Navigation & SLAM** (Mapping, path planning)

---

**Now go try the lessons!**

Start with: `robot lesson 3.1`

And work through 3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6

Have fun! 🤖
