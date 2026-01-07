# Chapter 4: Drive Systems - Getting Your Robot Moving

**Learn how robots move and control their motion**

In the previous chapters, you learned to control individual motors and make them work together. Now you'll learn how to make your robot move like a real mobile robot - with a high-level drive system that lets you think in terms of "go forward 1 meter" instead of "run motor 1 at 25 RPM."

---

## Table of Contents

1. [Theory: Types of Drive Systems](#theory-types-of-drive-systems)
2. [Coordinate Systems & Directions](#coordinate-systems--directions)
3. [Units & Conversions](#units--conversions)
4. [Understanding Your Mecanum Robot](#understanding-your-mecanum-robot)
5. [Building Your Drive System](#building-your-drive-system)
6. [Basic Velocity Control](#basic-velocity-control)
7. [Time-Based Movements](#time-based-movements)
8. [Distance-Based Movements with move_by()](#distance-based-movements-with-move_by)
9. [Calibration: Measuring and Improving Accuracy](#calibration-measuring-and-improving-accuracy)
10. [Movement Patterns](#movement-patterns)
11. [Keyboard Control (Teleoperation)](#keyboard-control-teleoperation)
12. [What's Next?](#whats-next)

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
- Position tracking happens in world frame (x, y, theta)

---

### Exercise 4.1: Coordinate Understanding 🧮

**Question 1:** Robot is facing East. You command `move(vx=0.3)`. Which direction does it go in the room?

<details>
<summary>Click for answer</summary>

East! Forward (vx) for the robot = East in the room since robot faces East.

</details>

---

**Question 2:** Robot is facing North and you want it to go East. Should you use vx or vy?

<details>
<summary>Click for answer</summary>

Use `vy` (strafe right with negative vy)!
- vx = forward = North (not what we want)
- vy = left/right = East/West (what we want!)

Or rotate the robot to face East first, then use vx.

</details>

---

**Question 3:** If robot faces Northeast (45°) and moves forward, which world coordinates change?

<details>
<summary>Click for answer</summary>

Both X and Y increase equally! Robot moves diagonally in world frame.

</details>

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

---

### Exercise 4.2: Unit Conversions 🧮

**Question 1:** Convert 75 cm to meters.

<details>
<summary>Answer</summary>

```python
meters = 75 / 100 = 0.75 m
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

## Understanding Your Mecanum Robot

Before programming, you need to understand your robot's physical setup.

### Mecanum Wheel Patterns

There are **two** common mecanum patterns. Your robot likely uses the **X pattern**.

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
from evabot.components.motors import Servo42D

# Test motor with CAN ID 1
motor = Servo42D(1)
motor.start()
motor.run(20)  # Slow speed

# Watch which wheel spins!
# Mark it with tape

import time
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

For accurate movement, you need to measure your robot:

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

### Exercise 4.3: Measure Your Robot 📏

Grab a ruler and measure:

1. **Wheel diameter:** _____ mm
   - Wheel radius = _____ mm = _____ m

2. **Wheelbase (front-to-back):** _____ mm = _____ m

3. **Track width (left-to-right):** _____ mm = _____ m

Write these down! You'll use them when creating your drive system.

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

# Start the robot (enables motors)
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
2. **Initializes tracking systems** (odometry starts in background)

From now on, you can command the robot to move!

---

## Basic Velocity Control

The fundamental way to control your mecanum robot is with **velocity commands**.

### The Three Velocities

Mecanum drive uses **three independent velocities**:

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

### Basic Movement Commands

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

### Important: Continuous Motion

**These commands set velocities - the robot keeps moving until you stop it!**

```python
robot.drive.forward(0.3)  # Starts moving forward
# Robot is still moving...
# Still moving...
robot.drive.halt()  # NOW it stops
```

This is different from "move forward 1 meter and stop" - we'll learn that next!

---

## Time-Based Movements

Sometimes you want to move for a specific **time** rather than a specific **distance**. This is simpler but less accurate.

### The `move_for()` Method

Your robot has a built-in method for time-based movements:

```python
robot.drive.move_for(duration, vx=?, vy=?, vtheta=?)
```

- `duration`: How long to move (seconds)
- `vx`, `vy`, `vtheta`: Velocities (same as `move()`)

**This blocks until the time expires**, then automatically stops!

---

### Basic Time-Based Movements

#### Move Forward for 5 Seconds

```python
# Move forward at 0.2 m/s for 5 seconds
robot.drive.move_for(5.0, vx=0.2)
print("Moved approximately 1 meter")  # 0.2 m/s × 5s = 1.0m
```

#### Rotate for 3 Seconds

```python
import math

# Rotate CCW at 0.5 rad/s for ~3.14 seconds (90°)
duration = (math.pi / 2) / 0.5  # angle / speed
robot.drive.move_for(duration, vtheta=0.5)
print("Rotated approximately 90 degrees")
```

#### Strafe Right for 3 Seconds

```python
# Strafe right at 0.15 m/s for 3.33 seconds
robot.drive.move_for(3.33, vy=-0.15)
print("Strafed approximately 0.5 meters")
```

---

### Combined Time-Based Movements

You can combine velocities:

```python
# Diagonal movement for 4 seconds
robot.drive.move_for(4.0, vx=0.2, vy=0.1)

# Forward while rotating for 3 seconds
robot.drive.move_for(3.0, vx=0.2, vtheta=0.3)

# All three for 5 seconds!
robot.drive.move_for(5.0, vx=0.2, vy=0.1, vtheta=0.2)
```

---

### Why "Approximately"?

Time-based movements are **approximate** because:
- 🔸 Floor friction varies (carpet vs tile)
- 🔸 Battery voltage drops as it drains
- 🔸 Wheels might slip
- 🔸 Motor speeds not perfectly matched
- 🔸 Acceleration/deceleration takes time

**Result:** You might be off by 5-10% or more!

**For accurate distance control, use `move_by()` instead (next section).**

---

### The Old Way (Still Works!)

Before `move_for()`, you had to do this manually:

```python
import time

# Manual time-based movement
robot.drive.forward(0.2)
time.sleep(5.0)
robot.drive.halt()
```

`move_for()` is just a convenience wrapper that does this for you!

---

## Distance-Based Movements with `move_by()`

Now let's move exact distances using the built-in `move_by()` method!

### The `move_by()` Method

Your robot's drive system has a powerful method that moves by **exact distances** using odometry feedback:

```python
robot.drive.move_by(dx=?, dy=?, dtheta=?)
```

- `dx`: Forward/backward distance in meters
- `dy`: Left/right distance in meters
- `dtheta`: Rotation angle in radians

**This is a blocking call** - it returns when the movement is complete!

---

### Basic Distance Movements

#### Move Forward 1 Meter

```python
import math

# Move forward exactly 1 meter
robot.drive.move_by(dx=1.0)
print("Moved forward 1 meter!")
```

#### Move Backward 0.5 Meters

```python
# Move backward 0.5 meters
robot.drive.move_by(dx=-0.5)
print("Moved backward 0.5 meters!")
```

#### Strafe Left 0.5 Meters

```python
# Strafe left 0.5 meters
robot.drive.move_by(dy=0.5)
print("Strafed left 0.5 meters!")
```

#### Strafe Right 0.3 Meters

```python
# Strafe right 0.3 meters
robot.drive.move_by(dy=-0.3)
print("Strafed right 0.3 meters!")
```

#### Rotate 90° Left (CCW)

```python
import math

# Rotate 90 degrees counter-clockwise
robot.drive.move_by(dtheta=math.pi/2)
print("Rotated 90° left!")
```

#### Rotate 45° Right (CW)

```python
import math

# Rotate 45 degrees clockwise
robot.drive.move_by(dtheta=-math.pi/4)
print("Rotated 45° right!")
```

---

### Combined Movements

The real power comes from combining movements!

#### Diagonal Movement

```python
# Move forward 1m and left 0.5m at the same time
robot.drive.move_by(dx=1.0, dy=0.5)
print("Moved diagonally!")
```

#### Forward While Rotating

```python
import math

# Move forward 1m while rotating 90° CCW
robot.drive.move_by(dx=1.0, dtheta=math.pi/2)
print("Forward + rotation complete!")
```

#### All Three at Once

```python
import math

# Forward + strafe + rotate simultaneously!
robot.drive.move_by(dx=1.0, dy=0.3, dtheta=math.pi/4)
print("Complex omnidirectional movement complete!")
```

---

### Why `move_by()` is Better Than Time-Based

**Time-based movement:**
```python
# Approximate - depends on floor, battery, etc.
robot.drive.forward(0.2)
time.sleep(5.0)  # Hope we go 1 meter...
robot.drive.halt()
```

**`move_by()` movement:**
```python
# Exact - uses encoder feedback!
robot.drive.move_by(dx=1.0)
# Stops exactly at 1 meter (±1cm accuracy)
```

**Advantages of `move_by()`:**
- ✅ **Accurate**: Uses odometry feedback, stops at exact position
- ✅ **Simple**: One line of code instead of calculating time
- ✅ **Automatic**: Handles speed control and stopping for you
- ✅ **Robust**: Adjusts if robot slips or gets pushed

---

### Adjusting Speed

You can control how fast the robot moves:

```python
# Slow movement (0.1 m/s)
robot.drive.move_by(dx=1.0, speed=0.1)

# Default speed (0.2 m/s)
robot.drive.move_by(dx=1.0)

# Faster movement (0.4 m/s)
robot.drive.move_by(dx=1.0, speed=0.4)
```

**Note:** Higher speeds may reduce accuracy slightly due to momentum!

---

### Resetting Your Origin with `zero_position()`

Sometimes you want to start fresh - treat your current location as the new origin point.

```python
# Robot is somewhere in the room
print(f"Current: {robot.odom.pose.x:.2f}, {robot.odom.pose.y:.2f}")
# Output: Current: 2.34, -1.12

# Reset this as the new origin
robot.drive.zero_position()

print(f"After reset: {robot.odom.pose.x:.2f}, {robot.odom.pose.y:.2f}")
# Output: After reset: 0.00, 0.00

# Now all movements are relative to this new origin
robot.drive.move_by(dx=1.0)
print(f"Position: {robot.odom.pose.x:.2f}")
# Output: Position: 1.00
```

**Use cases:**
- **Starting a new task**: "This is my starting point for this mission"
- **After manual repositioning**: Picked up robot and placed it somewhere new
- **Resetting for calibration**: Start calibration from a known zero point
- **Multi-stage tasks**: Reset between different task phases

**Example: Return to Origin**
```python
import math

# Mark starting point
robot.drive.zero_position()

# Drive somewhere
robot.drive.move_by(dx=2.0, dy=1.0)
robot.drive.move_by(dtheta=math.pi/2)

print(f"Somewhere else: x={robot.odom.pose.x:.2f}, y={robot.odom.pose.y:.2f}")

# Return to origin
robot.drive.move_by(dx=-robot.odom.pose.x, dy=-robot.odom.pose.y)
robot.drive.move_by(dtheta=-robot.odom.pose.theta)

print(f"Back home: x={robot.odom.pose.x:.3f}, y={robot.odom.pose.y:.3f}")
# Should be close to (0, 0) but not perfect due to drift!
```

---

## Calibration: Measuring and Improving Accuracy

Even `move_by()` depends on accurate robot measurements. Let's test and calibrate!

### Step 1: Test Current Accuracy

Let's see how accurate our 1-meter movement is:

```python
from evabot import Robot, MecanumDrive
import time

robot = Robot()
robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
robot.start()

time.sleep(1)

print("=" * 60)
print("Calibration Test: 1 Meter Forward")
print("=" * 60)
print()
print("Instructions:")
print("1. Mark robot's starting position with tape")
print("2. Press Enter to start")
print("3. Robot will move forward 1 meter")
print("4. Mark robot's ending position with tape")
print("5. Measure actual distance with ruler")
print()

input("Press Enter to start...")

# Move forward 1 meter using move_by()
print("\nMoving forward 1.0 meters...")

robot.drive.move_by(dx=1.0, speed=0.2)

print("\n" + "=" * 60)
print("Robot stopped!")
print("=" * 60)
print()
print("Now measure the actual distance between the two tape marks.")
print("The robot THINKS it moved 1.0 meters - but did it really?")
print()

robot.stop()
```

**Run this program and measure!**

---

### Step 2: Calculate Correction Factor

Let's say you measured **0.95 meters** but commanded **1.0 meters**.

```python
commanded_distance = 1.0  # meters (what we asked for)
measured_distance = 0.95  # meters (what actually happened)

# Calculate correction factor
correction = measured_distance / commanded_distance
# 0.95 / 1.0 = 0.95

print(f"Correction factor: {correction:.4f}")
```

This means wheels are slightly smaller than we thought (or there's friction, slip, etc.)

---

### Step 3: Update Wheel Radius

The most likely cause is wheel radius being slightly off:

```python
old_radius = 0.050  # 50mm (current setting)
new_radius = old_radius * correction
# 0.050 × 0.95 = 0.0475 meters (47.5mm)

print(f"Old wheel radius: {old_radius*1000:.1f} mm")
print(f"New wheel radius: {new_radius*1000:.1f} mm")
print()
print(f"Update your code:")
print(f"robot.drive = MecanumDrive(..., wheel_radius={new_radius:.4f})")
```

---

### Step 4: Test Again with New Value

```python
robot.drive = MecanumDrive(
    fl=4, fr=2, bl=3, br=1,
    wheel_radius=0.0475,  # ← Updated value!
)
robot.start()

# Run the 1-meter test again
# Should be much more accurate now!
```

---

### Step 5: Iterate If Needed

You might need 2-3 iterations to get it perfect:

1. **First test:** Commanded 1.0m, got 0.95m → adjust to 0.0475
2. **Second test:** Commanded 1.0m, got 0.98m → adjust to 0.0466
3. **Third test:** Commanded 1.0m, got 0.995m → close enough! ✓

---

### Calibration for Rotation

Same process for rotation:

```python
import math

# Test: Rotate 360° (full circle)
print("Rotating 360 degrees...")
robot.drive.move_by(dtheta=2*math.pi, speed=0.2)

# Check: Did robot complete full circle?
# Mark starting orientation, check if it returned to same angle
# - If it rotated MORE than 360°: wheelbase/track_width too large
# - If it rotated LESS than 360°: wheelbase/track_width too small
```

Adjust `wheel_base` and `track_width` parameters slightly to fix rotation accuracy.

---

### Practical Calibration Tips

1. **Use a long distance** for calibration (1 meter or more)
   - Errors are easier to measure
   - Percentage accuracy improves

2. **Test on the floor you'll use**
   - Carpet vs tile makes a difference
   - Calibrate for your main environment

3. **Check battery level**
   - Low battery = lower speeds
   - Calibrate with fresh battery

4. **Measure carefully**
   - Use a good ruler or measuring tape
   - Measure from same point on robot (center)

5. **Multiple trials**
   - Run test 3 times, average the results
   - Reduces random error

---

## Movement Patterns

Now let's create interesting patterns with our calibrated robot using `move_by()`!

### Pattern 1: Drive a Square

```python
import math
import time

# Drive a 1m × 1m square
print("Driving a square...")

for i in range(4):
    print(f"Side {i+1}:")

    # Forward 1 meter
    robot.drive.move_by(dx=1.0, speed=0.2)
    time.sleep(0.5)  # Brief pause

    # Turn left 90°
    robot.drive.move_by(dtheta=math.pi/2, speed=0.2)
    time.sleep(0.5)

print("Square complete!")
```

**Challenge:** After completing the square, check the robot's position. Did it return exactly to start? This shows odometry drift!

---

### Pattern 2: Star Pattern

```python
import math
import time

print("Drawing a star...")

# 5-pointed star: forward, turn 144°, repeat
for i in range(5):
    print(f"Point {i+1}:")

    # Forward 0.8 meters
    robot.drive.move_by(dx=0.8, speed=0.2)
    time.sleep(0.3)

    # Turn 144° (360°/5 × 2)
    angle = math.radians(144)
    robot.drive.move_by(dtheta=angle, speed=0.2)
    time.sleep(0.3)

print("Star complete!")
```

---

### Pattern 3: Spiral Outward

```python
import math
import time

print("Driving a spiral...")

# Start small, get bigger
distance = 0.2  # Start with 20cm

for i in range(8):
    print(f"Loop {i+1}: {distance:.2f}m")

    # Forward
    robot.drive.move_by(dx=distance, speed=0.2)

    # Turn 90°
    robot.drive.move_by(dtheta=math.pi/2, speed=0.2)

    # Increase distance
    distance += 0.1

print("Spiral complete!")
```

---

### Pattern 4: Zigzag

```python
import math
import time

print("Driving zigzag...")

for i in range(6):
    # Forward
    robot.drive.move_by(dx=0.5, speed=0.2)

    # Alternate left and right strafe
    if i % 2 == 0:
        robot.drive.move_by(dy=0.3, speed=0.2)  # Strafe left
    else:
        robot.drive.move_by(dy=-0.3, speed=0.2)  # Strafe right

    time.sleep(0.3)

print("Zigzag complete!")
```

---

### Pattern 5: Circle (Using Continuous Motion)

For smooth curves, we still use velocity control:

```python
import time

print("Driving a circle...")

# Drive forward while rotating
# Adjust speeds to change circle size
robot.drive.move(vx=0.2, vy=0, vtheta=0.3)
time.sleep(20)  # ~One circle

robot.drive.halt()
print("Circle complete!")
```

**Note:** Smooth curves are better with continuous velocity control than discrete `move_by()` steps!

---

## Keyboard Control (Teleoperation)

Now for the fun part - control your robot like an RC car!

### Simple Keyboard Control

```python
#!/usr/bin/env python3
"""
Simple keyboard control for EvaBot.

Controls:
    W/S: Forward/Backward
    A/D: Strafe Left/Right
    Q/E: Rotate Left/Right
    Space: Stop
    X: Exit
"""

from evabot import Robot, MecanumDrive
import sys
import tty
import termios

def get_key():
    """Read a single keypress from terminal."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

def main():
    # Create robot
    robot = Robot()
    robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
    robot.start()

    # Control parameters
    linear_speed = 0.3  # m/s
    rotation_speed = 0.5  # rad/s

    print("=" * 60)
    print("EvaBot Keyboard Control")
    print("=" * 60)
    print()
    print("Controls:")
    print("  W/S: Forward/Backward")
    print("  A/D: Strafe Left/Right")
    print("  Q/E: Rotate Left/Right")
    print("  Space: Stop")
    print("  X: Exit")
    print()
    print("Press keys to control robot...")
    print()

    try:
        while True:
            key = get_key().lower()

            if key == 'w':
                print("Forward")
                robot.drive.forward(linear_speed)

            elif key == 's':
                print("Backward")
                robot.drive.backward(linear_speed)

            elif key == 'a':
                print("Strafe Left")
                robot.drive.strafe_left(linear_speed)

            elif key == 'd':
                print("Strafe Right")
                robot.drive.strafe_right(linear_speed)

            elif key == 'q':
                print("Rotate Left (CCW)")
                robot.drive.rotate_ccw(rotation_speed)

            elif key == 'e':
                print("Rotate Right (CW)")
                robot.drive.rotate_cw(rotation_speed)

            elif key == ' ':
                print("Stop")
                robot.drive.halt()

            elif key == 'x':
                print("Exiting...")
                break

            elif key == '\x03':  # Ctrl+C
                break

    except KeyboardInterrupt:
        pass

    finally:
        print("\nStopping robot...")
        robot.drive.halt()
        robot.stop()
        print("Done!")

if __name__ == "__main__":
    main()
```

**Try it!** Save as `keyboard_control.py` and run:
```bash
python keyboard_control.py
```

---

### Advanced: Speed Control

Add number keys to change speed:

```python
# In the main loop, add:

elif key in '123456789':
    # Change speed with number keys
    level = int(key)
    linear_speed = level * 0.1
    rotation_speed = level * 0.1
    print(f"Speed level {level}: {linear_speed} m/s")

elif key == '0':
    # Reset to default
    linear_speed = 0.3
    rotation_speed = 0.5
    print(f"Speed reset: {linear_speed} m/s")
```

---

### Challenge: Combined Movement

Can you add diagonal movement keys?

```python
elif key == 'r':  # Forward-right diagonal
    print("Forward-Right")
    robot.drive.move(vx=linear_speed, vy=-linear_speed*0.5, vtheta=0)

elif key == 't':  # Forward-left diagonal
    print("Forward-Left")
    robot.drive.move(vx=linear_speed, vy=linear_speed*0.5, vtheta=0)

# Add more combinations!
```

---

## What's Next?

You've learned command-based control with `move_by()` - the robot handles the feedback internally. But what if YOU want to read sensors and make decisions?

**Example:** Right now you use:
```python
robot.drive.move_by(dx=1.0)  # Robot handles everything
```

**But what if you want to:**
- Stop when you see a wall (using lidar)?
- Follow a colored object (using camera)?
- Drive until reaching a specific GPS coordinate?
- Implement your own advanced controller?

**That requires reading sensors and writing your own control loops!**

---

### Chapter 5: User-Written Control Loops (Coming Next!)

In Chapter 5, you'll learn:

- **Reading odometry**: Access `robot.odom.pose.x/y/theta` in your code
- **Writing feedback loops**: Check sensors, make decisions
- **Custom behaviors**: Implement your own movement strategies
- **Understanding drift**: Why odometry isn't perfect over long distances

**Example of what's coming:**
```python
# YOU write the control logic!
start_x = robot.odom.pose.x

while robot.odom.pose.x - start_x < 1.0:
    # Check if we should keep going
    if robot.lidar.front < 30:  # Wall ahead!
        print("Wall detected, stopping!")
        break

    robot.drive.forward(0.3)
    time.sleep(0.01)

robot.drive.halt()
```

You'll learn to **read all available sensors** and **write intelligent control logic** - becoming a real robotics programmer!

---

## Summary

In this chapter you learned:

✅ **Theory:**
- Types of drive systems (differential, mecanum, ackermann)
- Coordinate systems (robot frame vs world frame)
- Unit conversions (m/s, rad/s, degrees, radians)

✅ **Hardware:**
- Identify motor IDs and wheel patterns (X vs Diamond)
- Measure robot dimensions
- Build MecanumDrive object

✅ **Control:**
- **Velocity control**: `robot.drive.move(vx, vy, vtheta)` for continuous motion
- **Time-based control**: `robot.drive.move_for(duration, vx, vy, vtheta)` - simple but approximate
- **Distance control**: `robot.drive.move_by(dx, dy, dtheta)` - accurate with feedback
- **Reset origin**: `robot.drive.zero_position()` - start fresh from current location
- Combining movements (forward + strafe + rotate simultaneously!)

✅ **Calibration:**
- Test actual vs expected distance
- Calculate correction factors
- Update wheel_radius parameter
- Improve accuracy through iterative testing

✅ **Patterns:**
- Square, star, spiral, zigzag patterns
- Smooth curves with velocity control
- Combining movements creatively

✅ **Teleoperation:**
- Keyboard control (WASD + QE)
- Real-time manual control
- Speed adjustment

**Key Takeaway:** You learned **command-based control** - tell the robot what to do, and it handles the details. In Chapter 5, you'll learn to read sensors and write your own control logic!

---

**Now go try the lessons!**

Start with: `robot lesson 3.1`

And work through 3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6

Have fun! 🤖
