# Chapter 4: Mecanum Drive and Lidar Basics

**Learn to drive your robot and sense walls**

In this chapter, you'll learn the basics of controlling your mecanum robot and using the lidar to detect obstacles.

---

## What You'll Learn

1. Create a mecanum drive
2. Drive forward, strafe, and rotate
3. Read where the robot is (odometry)
4. Stop after moving a distance
5. Use lidar to stop before a wall

---

## Why Use Robot()?

You might wonder: why create a `Robot()` and add components to it? Why not just control motors directly?

**The Robot manages everything:**
```python
robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2)
robot.lidar = RPLidarC1()
robot.start()  # ← Starts ALL components together!
```

**Benefits:**
- **One start/stop** - All components start and stop together
- **Shared connections** - Components can talk to each other (drive can use lidar data)
- **Automatic cleanup** - When you stop the robot, everything stops cleanly
- **Simpler code** - One object instead of many separate parts

**Without Robot (harder way):**
```python
# You'd have to manage each motor separately
motor1 = Servo42D(1)
motor2 = Servo42D(2)
motor3 = Servo42D(3)
motor4 = Servo42D(4)
lidar = RPLidarC1()

# Start each one
motor1.start()
motor2.start()
motor3.start()
motor4.start()
lidar.start()

# Calculate what each motor should do...
# This is complicated!
```

The `Robot()` object makes robotics simple - it handles the complex stuff so you can focus on making your robot do cool things!

---

## Creating the Mecanum Drive

Your robot has 4 wheels that can move in any direction. Let's set it up.

### Motor Configuration

First, you need to know which motor is which. The motors are labeled FL (front-left), FR (front-right), BL (back-left), BR (back-right).

**Find your motor IDs:**
```python
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()
```

The numbers (3, 4, 1, 2) are the CAN IDs. Your robot might be different - check the labels on your motors.

---

## Basic Movements

Now let's make the robot move!

### Forward and Backward

```python
import time
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

# Move forward
robot.drive.move(vx=0.2)  # 0.2 m/s forward
time.sleep(2)  # Move for 2 seconds

# Stop
robot.drive.halt()

robot.stop()
```

**What this does:**
- `vx=0.2` means move forward at 0.2 meters per second
- `vx=-0.2` would move backward
- `time.sleep(2)` waits 2 seconds while the robot moves
- `halt()` stops the robot

---

### Strafe Left and Right

Mecanum wheels can move sideways without turning!

```python
import time
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

# Strafe left
robot.drive.move(vy=0.2)  # 0.2 m/s left
time.sleep(2)

robot.drive.halt()

robot.stop()
```

**What this does:**
- `vy=0.2` means strafe left at 0.2 m/s
- `vy=-0.2` would strafe right

---

### Rotate in Place

```python
import time
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

# Rotate counter-clockwise
robot.drive.move(vtheta=0.5)  # 0.5 rad/s
time.sleep(2)

robot.drive.halt()

robot.stop()
```

**What this does:**
- `vtheta=0.5` means rotate counter-clockwise at 0.5 radians per second
- `vtheta=-0.5` would rotate clockwise

---

### Exercise 4.1: Move in All Directions

Make the robot:
1. Move forward for 2 seconds
2. Strafe right for 2 seconds
3. Move backward for 2 seconds
4. Strafe left for 2 seconds

<details>
<summary>Solution</summary>

```python
import time
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

robot.drive.move(vx=0.2)
time.sleep(2)
robot.drive.halt()
time.sleep(0.5)

robot.drive.move(vy=-0.2)
time.sleep(2)
robot.drive.halt()
time.sleep(0.5)

robot.drive.move(vx=-0.2)
time.sleep(2)
robot.drive.halt()
time.sleep(0.5)

robot.drive.move(vy=0.2)
time.sleep(2)
robot.drive.halt()

robot.stop()
```

</details>

---

## Moving for Time

Instead of using `time.sleep()`, you can tell the robot to move for a specific time.

### Using move_for()

```python
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

# Move forward for 3 seconds
robot.drive.move_for(3.0, vx=0.2)

# Move left for 2 seconds
robot.drive.move_for(2.0, vy=0.2)

# Rotate for 1.5 seconds
robot.drive.move_for(1.5, vtheta=0.5)

robot.stop()
```

**What this does:**
- `move_for(3.0, vx=0.2)` moves forward at 0.2 m/s for 3 seconds, then stops automatically
- No need to call `halt()` - it stops when time is up
- Simpler than using `time.sleep()`!

---

### Exercise 4.2: Square with move_for()

Make the robot drive a square using `move_for()`:
- Each side: 2 seconds forward
- Each turn: 1.6 seconds rotation

<details>
<summary>Solution</summary>

```python
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

for i in range(4):
    robot.drive.move_for(2.0, vx=0.2)
    robot.drive.move_for(1.6, vtheta=0.5)

robot.stop()
```

</details>

---

## Reading Odometry

The robot tracks where it is by counting wheel rotations. This is called **odometry**.

### Check the Robot's Position

```python
import time
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

time.sleep(1)  # Let odometry initialize

# Move forward
robot.drive.move(vx=0.2)

# Watch position update
for i in range(20):
    x = robot.odom.pose.x
    print(f"Position: {x:.2f} m")
    time.sleep(0.2)

robot.drive.halt()
robot.stop()
```

**What this shows:**
- `robot.odom.pose.x` is the forward/backward position in meters
- `robot.odom.pose.y` is the left/right position
- `robot.odom.pose.theta` is the rotation angle

---

## Moving by Distance

Instead of using time or writing loops, you can tell the robot to move an exact distance.

### Using move_by()

```python
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

# Move forward exactly 1 meter
robot.drive.move_by(dx=1.0)

# Move backward 0.5 meters
robot.drive.move_by(dx=-0.5)

# Strafe left 0.3 meters
robot.drive.move_by(dy=0.3)

# Rotate 90 degrees (1.57 radians)
robot.drive.move_by(dtheta=1.57)

robot.stop()
```

**What this does:**
- `move_by(dx=1.0)` moves forward exactly 1 meter, then stops
- Uses odometry to know when to stop
- Much more accurate than time-based movement!

---

### Exercise 4.3: Square with move_by()

Make the robot drive a 0.5m × 0.5m square using `move_by()`:
- Each side: 0.5 meters
- Each turn: 1.57 radians (90 degrees)

<details>
<summary>Solution</summary>

```python
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

for i in range(4):
    robot.drive.move_by(dx=0.5)
    robot.drive.move_by(dtheta=1.57)

robot.stop()
```

</details>

---

## Stop by Distance (Manual Loop)

Sometimes `move_by()` isn't enough - you need to check sensors while moving. Let's learn to write your own loop.

### Simple Distance Loop

```python
import time
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

time.sleep(1)

# Remember starting position
start_x = robot.odom.pose.x

# Start moving
robot.drive.move(vx=0.2)

# Keep checking until we've moved 1 meter
while True:
    current_x = robot.odom.pose.x
    distance = current_x - start_x

    if distance >= 1.0:
        break

    time.sleep(0.01)

# Stop
robot.drive.halt()

print(f"Moved {distance:.2f} meters")
robot.stop()
```

**How it works:**
1. Remember where we started (`start_x`)
2. Start moving forward
3. Keep checking current position in a loop
4. When we've moved 1 meter, break out of loop
5. Stop the robot

**Why write your own loop?**
- When you need to check lidar while moving
- When you need custom stopping conditions
- To learn how control works!

---

### Exercise 4.4: Move 0.5 Meters with Loop

Write your own loop to move exactly 0.5 meters forward.

<details>
<summary>Solution</summary>

```python
import time
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

time.sleep(1)

start_x = robot.odom.pose.x
robot.drive.move(vx=0.2)

while True:
    distance = robot.odom.pose.x - start_x
    if distance >= 0.5:
        break
    time.sleep(0.01)

robot.drive.halt()
robot.stop()
```

</details>

---

## Lidar Coordinate System

Before using the lidar, you need to understand how it measures angles.

### Robot Coordinates vs Lidar Angles

**Robot coordinate system:**
```
        FRONT
         ↑ vx (forward)
         |
    FL  |  FR
      \ | /
       \|/
  vy ←--●      Robot center
       /|\
      / | \
    BL  |  BR
         |
        BACK
```

- `vx` = forward/backward
- `vy` = left/right
- Robot thinks in terms of "forward", "left", etc.

**Lidar coordinate system:**
```
        0° (FRONT)
         |
         |
270° ----●---- 90°
   (LEFT)     (RIGHT)
         |
         |
       180° (BACK)
```

- Lidar measures angles in degrees
- **0°** = straight ahead (same as robot's forward)
- **90°** = to the right
- **180°** = behind
- **270°** = to the left
- Angles increase **clockwise** (CW): 0° → 90° → 180° → 270° → 360°(=0°)

**Key point:** The lidar spins on top of your robot and measures distances at different angles. When you ask for angle `0`, you get the distance straight ahead. Angle `90` is to the right, and so on.

---

## Adding Lidar

The lidar sensor spins around and measures distances to walls and objects.

### Setup Lidar

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)  # Let lidar initialize

# Check distance in front
distance = robot.lidar.get_distance_at_angle(0)
if distance:
    print(f"Distance ahead: {distance:.2f} m")

robot.stop()
```

**Remember the angles:**
- `0` = front, `90` = right, `180` = back, `270` = left
- `get_distance_at_angle()` returns distance in meters, or `None` if no reading

---

## Stop Before a Wall

Now let's drive forward and stop before hitting a wall.

### Simple Wall Approach

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Start moving
robot.drive.move(vx=0.1)

# Keep checking distance
while True:
    distance = robot.lidar.get_distance_at_angle(0)

    if distance and distance < 0.30:  # Stop at 30cm
        break

    time.sleep(0.05)

# Stop
robot.drive.halt()

robot.stop()
```

**How it works:**
1. Start moving forward slowly (0.1 m/s)
2. Keep checking distance to wall at angle 0 (straight ahead)
3. When distance < 0.30 meters (30cm), stop
4. This prevents collision!

---

### Exercise 4.5: Approach from All Sides

Make the robot:
1. Move forward until 30cm from front wall
2. Move backward until 30cm from back wall
3. Strafe left until 30cm from left wall
4. Strafe right until 30cm from right wall

<details>
<summary>Solution</summary>

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Forward
robot.drive.move(vx=0.1)
while True:
    d = robot.lidar.get_distance_at_angle(0)
    if d and d < 0.30:
        break
    time.sleep(0.05)
robot.drive.halt()
time.sleep(1)

# Backward
robot.drive.move(vx=-0.1)
while True:
    d = robot.lidar.get_distance_at_angle(180)
    if d and d < 0.30:
        break
    time.sleep(0.05)
robot.drive.halt()
time.sleep(1)

# Left
robot.drive.move(vy=0.1)
while True:
    d = robot.lidar.get_distance_at_angle(270)
    if d and d < 0.30:
        break
    time.sleep(0.05)
robot.drive.halt()
time.sleep(1)

# Right
robot.drive.move(vy=-0.1)
while True:
    d = robot.lidar.get_distance_at_angle(90)
    if d and d < 0.30:
        break
    time.sleep(0.05)
robot.drive.halt()

robot.stop()
```

</details>

---

## Combining Movement and Sensing

You can combine different velocities and check multiple sensors.

### Move Diagonally

```python
import time
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

# Move forward AND left at the same time
robot.drive.move(vx=0.2, vy=0.2)
time.sleep(2)

robot.drive.halt()
robot.stop()
```

### Drive a Square

```python
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

for i in range(4):
    robot.drive.move_by(dx=0.5)
    robot.drive.move_by(dtheta=1.57)

robot.stop()
```

---

### Exercise 4.6: Spiral Pattern

Make the robot drive in a growing spiral:
- Start with 0.2m forward
- Each side gets 0.1m longer
- Do 6 sides total

<details>
<summary>Solution</summary>

```python
from evabot import Robot, MecanumDrive

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.start()

distance = 0.2
for i in range(6):
    robot.drive.move_by(dx=distance)
    robot.drive.move_by(dtheta=1.57)
    distance += 0.1

robot.stop()
```

</details>

---

## Summary

You learned:

✅ Create mecanum drive with 4 motors
✅ Basic movements: forward, strafe, rotate with `move()`
✅ Time-based movement with `move_for()` - simple and automatic
✅ Read odometry (position tracking)
✅ Distance-based movement with `move_by()` - accurate and automatic
✅ Write your own loop for custom control
✅ Add lidar sensor
✅ Stop before walls using lidar
✅ Combine movements for patterns

**Three ways to move:**
```python
# 1. Manual control (you call halt)
robot.drive.move(vx=0.2)
time.sleep(2)
robot.drive.halt()

# 2. Time-based (automatic stop)
robot.drive.move_for(2.0, vx=0.2)

# 3. Distance-based (automatic stop)
robot.drive.move_by(dx=0.5)
```

**Pattern for custom control with lidar:**
```python
# Start moving
robot.drive.move(vx=0.1)

# Check sensor in a loop
while True:
    distance = robot.lidar.get_distance_at_angle(0)
    if distance and distance < 0.30:
        break
    time.sleep(0.05)

# Stop
robot.drive.halt()
```

---

## What's Next?

Chapter 5 will teach you more advanced lidar control:
- Use `check_wall()` to align parallel to walls
- Use `get_clearance()` for safer obstacle detection
- Make the robot follow walls
- Navigate around a square room

Ready? Let's go! 🤖
