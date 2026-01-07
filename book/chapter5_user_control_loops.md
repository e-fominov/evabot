# Chapter 5: Writing Your Own Control Loops

**Learn to read sensors and make decisions**

In Chapter 4, you learned command-based control - tell the robot what to do, and it handles everything:

```python
robot.drive.move_by(dx=1.0)  # Robot figures out how to get there
```

But what if YOU want to make decisions based on what the robot senses? What if you want to:
- Stop when you detect a wall?
- Follow a moving object?
- Implement your own custom movement strategy?

**That's what this chapter is about** - reading sensors and writing control logic!

---

## Table of Contents

1. [Reading Odometry](#reading-odometry)
2. [Your First Control Loop](#your-first-control-loop)
3. [Proportional Control](#proportional-control)
4. [When to Use Built-in vs User-Written Control](#when-to-use-built-in-vs-user-written-control)
5. [Practical Examples](#practical-examples)
6. [What's Next: Adding More Sensors](#whats-next-adding-more-sensors)

---

## Reading Odometry

Your robot tracks its position using **odometry** - measuring wheel rotations to calculate where it is.

### Accessing the Odometry Data

```python
# Access position (where the robot is)
x = robot.odom.pose.x          # meters (forward/backward in world frame)
y = robot.odom.pose.y          # meters (left/right in world frame)
theta = robot.odom.pose.theta  # radians (orientation angle)

# Access velocity (how fast the robot is moving)
vx = robot.odom.velocity.vx          # m/s (forward speed)
vy = robot.odom.velocity.vy          # m/s (sideways speed)
vtheta = robot.odom.velocity.vtheta  # rad/s (rotation speed)
```

---

### Monitoring Position While Moving

Let's watch the robot's position update in real-time:

```python
import time

# Start moving
robot.drive.forward(0.2)

# Monitor for 5 seconds
for i in range(50):
    pose = robot.odom.pose
    print(f"Position: x={pose.x:.3f}m, y={pose.y:.3f}m, θ={pose.theta:.3f}rad")
    time.sleep(0.1)  # Update 10 times per second

robot.drive.halt()
```

**Try this!** You'll see the position updating smoothly as the robot moves.

---

### Understanding the Updates

The odometry system updates **50 times per second** in the background. Every 20 milliseconds:

1. Reads encoder positions from all 4 motors
2. Calculates how much each wheel moved
3. Converts wheel motion to robot motion (dx, dy, dtheta)
4. Updates position in world frame

**You don't have to do any of this** - just read `robot.odom.pose` whenever you want!

---

## Your First Control Loop

Now let's write YOUR OWN control loop to move exactly 1 meter.

### The Goal

Instead of:
```python
robot.drive.move_by(dx=1.0)  # Easy but you don't control it
```

You write:
```python
# YOU control when to stop!
start_x = robot.odom.pose.x

robot.drive.forward(0.2)

while robot.odom.pose.x - start_x < 1.0:
    time.sleep(0.01)  # Check 100 times/second

robot.drive.halt()
```

---

### Step-by-Step Breakdown

```python
import time

# Step 1: Remember starting position
start_x = robot.odom.pose.x
print(f"Starting at x={start_x:.3f}m")

# Step 2: Start moving forward
robot.drive.forward(0.2)  # 0.2 m/s

# Step 3: Keep checking until we've gone 1 meter
while True:
    # Calculate how far we've traveled
    current_x = robot.odom.pose.x
    distance_traveled = current_x - start_x

    # Are we there yet?
    if distance_traveled >= 1.0:
        break  # Exit the loop!

    # Not there yet, keep checking
    time.sleep(0.01)  # Check every 10ms

# Step 4: Stop moving
robot.drive.halt()

print(f"Traveled {distance_traveled:.3f} meters!")
```

---

### Why Write Your Own Loop?

**Advantages:**
- ✅ You can add custom logic (check sensors, adjust speed, etc.)
- ✅ You understand exactly what's happening
- ✅ You can stop based on ANY condition (not just distance)
- ✅ Full control over the movement strategy

**Disadvantages:**
- ❌ More code to write
- ❌ You have to handle stopping correctly
- ❌ Need to understand control concepts

**For simple movements, use `move_by()`. For custom behaviors, write your own loop!**

---

### Exercise 5.1: Move 0.5 Meters Your Way

Try writing a loop to move exactly 0.5 meters:

```python
import time

# TODO: Remember starting position


# TODO: Start moving forward


# TODO: Loop until 0.5 meters traveled
while True:
    # Calculate distance traveled


    # Check if reached target


    time.sleep(0.01)

# TODO: Stop


print("Done!")
```

<details>
<summary>Click for solution</summary>

```python
import time

start_x = robot.odom.pose.x

robot.drive.forward(0.2)

while True:
    current_x = robot.odom.pose.x
    distance = current_x - start_x

    if distance >= 0.5:
        break

    time.sleep(0.01)

robot.drive.halt()

print("Done!")
```

</details>

---

## Proportional Control

Your first control loop works, but it has a problem: the robot moves at **full speed until the last moment**, then stops abruptly. This can cause:
- Overshoot (going past the target)
- Jerky motion
- Wear on motors

**Better idea:** Slow down as you approach the target!

---

### The Proportional Control Concept

**Proportional control** means: speed proportional to distance remaining.

- Far from target → fast speed
- Close to target → slow speed
- At target → stop

```
Speed = K × (distance remaining)

K = proportional gain (how aggressive)
```

---

### Simple Proportional Control Example

```python
import time

start_x = robot.odom.pose.x
target_distance = 1.0  # 1 meter

while True:
    # Calculate distance remaining
    current_x = robot.odom.pose.x
    distance_traveled = current_x - start_x
    distance_remaining = target_distance - distance_traveled

    # Are we close enough?
    if distance_remaining < 0.01:  # 1cm threshold
        break

    # Calculate speed proportional to distance remaining
    # K = 0.5 means: at 1m away, speed = 0.5 m/s
    #                at 0.5m away, speed = 0.25 m/s
    #                at 0.1m away, speed = 0.05 m/s
    K = 0.5
    speed = K * distance_remaining

    # Limit speed (don't go too fast or too slow)
    speed = max(0.05, min(0.3, speed))  # Between 0.05 and 0.3 m/s

    # Update robot speed
    robot.drive.forward(speed)

    time.sleep(0.01)

robot.drive.halt()
print("Arrived smoothly!")
```

---

### Comparing the Two Approaches

**Constant speed:**
```python
robot.drive.forward(0.2)  # Always 0.2 m/s
while distance < target:
    time.sleep(0.01)
robot.drive.halt()
```
- Simple
- Abrupt stop
- May overshoot

**Proportional control:**
```python
while distance_remaining > threshold:
    speed = K * distance_remaining
    speed = max(min_speed, min(max_speed, speed))  # Clamp
    robot.drive.forward(speed)
    time.sleep(0.01)
robot.drive.halt()
```
- Smoother
- Gradual slowdown
- More accurate

---

### Exercise 5.2: Proportional Control to 2 Meters

Implement proportional control to move 2 meters:

```python
import time

start_x = robot.odom.pose.x
target_distance = 2.0

while True:
    current_x = robot.odom.pose.x
    distance_traveled = current_x - start_x
    distance_remaining = target_distance - distance_traveled

    # TODO: Check if close enough (within 1cm)


    # TODO: Calculate proportional speed (K = 0.4)


    # TODO: Limit speed between 0.05 and 0.3 m/s


    # TODO: Set robot speed


    time.sleep(0.01)

robot.drive.halt()
```

<details>
<summary>Click for solution</summary>

```python
import time

start_x = robot.odom.pose.x
target_distance = 2.0

while True:
    current_x = robot.odom.pose.x
    distance_traveled = current_x - start_x
    distance_remaining = target_distance - distance_traveled

    if distance_remaining < 0.01:
        break

    K = 0.4
    speed = K * distance_remaining

    speed = max(0.05, min(0.3, speed))

    robot.drive.forward(speed)

    time.sleep(0.01)

robot.drive.halt()
```

</details>

---

## When to Use Built-in vs User-Written Control

Now you know both approaches. When should you use each?

### Use Built-in Methods When:

**`move_by()` - Distance-based:**
```python
robot.drive.move_by(dx=1.0)
```
✅ You just want to move a specific distance
✅ No special conditions or logic needed
✅ Accuracy is important
✅ You want simple, clean code

**`move_for()` - Time-based:**
```python
robot.drive.move_for(5.0, vx=0.2)
```
✅ You care about time, not exact distance
✅ Simple timed movements
✅ Quick prototyping

---

### Write Your Own Loop When:

```python
while condition:
    # Your logic here
    robot.drive.forward(speed)
    time.sleep(0.01)
robot.drive.halt()
```

✅ You need to check sensors (lidar, camera, etc.)
✅ You want custom speed control
✅ Multiple stopping conditions
✅ Complex decision-making
✅ Learning how control works

---

### Decision Guide

**Ask yourself:**

1. **"Do I just need to move from A to B?"**
   → Use `move_by()`

2. **"Do I need to check sensors or make decisions while moving?"**
   → Write your own loop

3. **"Do I want smooth speed control?"**
   → Write your own loop with proportional control

4. **"Am I learning about control systems?"**
   → Write your own loop!

---

### Example Comparison

**Task:** Move forward 1 meter

**Built-in way:**
```python
robot.drive.move_by(dx=1.0)  # 1 line, done!
```

**Your way (simple):**
```python
start = robot.odom.pose.x
robot.drive.forward(0.2)
while robot.odom.pose.x - start < 1.0:
    time.sleep(0.01)
robot.drive.halt()  # 5 lines
```

**Your way (proportional):**
```python
start = robot.odom.pose.x
while True:
    remaining = 1.0 - (robot.odom.pose.x - start)
    if remaining < 0.01:
        break
    speed = max(0.05, min(0.3, 0.5 * remaining))
    robot.drive.forward(speed)
    time.sleep(0.01)
robot.drive.halt()  # 9 lines, smoother
```

**Each has its place!**

---

## Practical Examples

Let's see some real-world uses of user-written control loops.

### Example 1: Move to Specific World Position

Move to `x = 2.0` meters in world frame (regardless of starting position):

```python
import time

target_x = 2.0

while True:
    current_x = robot.odom.pose.x
    error = target_x - current_x

    # Close enough?
    if abs(error) < 0.01:
        break

    # Proportional control (works for both directions!)
    K = 0.5
    speed = K * error  # Positive if need to go forward, negative if backward

    # Limit speed
    speed = max(-0.3, min(0.3, speed))

    # Apply speed (vx can be negative!)
    robot.drive.move(vx=speed)

    time.sleep(0.01)

robot.drive.halt()
print(f"Arrived at x={robot.odom.pose.x:.3f}m")
```

**This works whether you're behind OR ahead of the target!**

---

### Example 2: Rotate to Face East

Rotate until facing East (θ = 0 radians):

```python
import time
import math

target_theta = 0.0  # Face East

while True:
    current_theta = robot.odom.pose.theta
    error = target_theta - current_theta

    # Normalize angle error to [-pi, pi]
    while error > math.pi:
        error -= 2 * math.pi
    while error < -math.pi:
        error += 2 * math.pi

    # Close enough?
    if abs(error) < 0.05:  # ~3 degrees
        break

    # Proportional rotation
    K = 0.8
    rotation_speed = K * error

    # Limit speed
    rotation_speed = max(-0.5, min(0.5, rotation_speed))

    robot.drive.move(vtheta=rotation_speed)

    time.sleep(0.01)

robot.drive.halt()
print(f"Facing θ={robot.odom.pose.theta:.3f}rad ({math.degrees(robot.odom.pose.theta):.1f}°)")
```

---

### Example 3: Drive in a Circle Around Origin

Maintain 0.5 meter distance from origin while driving in a circle:

```python
import time
import math

# Drive for 20 seconds
start_time = time.time()

while time.time() - start_time < 20.0:
    # Calculate distance from origin
    x = robot.odom.pose.x
    y = robot.odom.pose.y
    distance = math.sqrt(x**2 + y**2)

    target_distance = 0.5  # Stay 0.5m from origin
    error = distance - target_distance

    # If too far, move inward (negative vy strafes right/inward)
    # If too close, move outward (positive vy strafes left/outward)
    K_strafe = -0.3
    vy = K_strafe * error
    vy = max(-0.15, min(0.15, vy))

    # Also rotate to go around the circle
    vtheta = 0.3  # Constant rotation

    robot.drive.move(vx=0, vy=vy, vtheta=vtheta)

    time.sleep(0.05)  # 20 Hz control

robot.drive.halt()
print("Circle complete!")
```

**This maintains distance while circling - two things at once!**

---

### Example 4: Stop Based on Two Conditions

Move forward until EITHER:
- Reached 1 meter, OR
- (Future: Wall detected - placeholder for Chapter 6)

```python
import time

start_x = robot.odom.pose.x
target_distance = 1.0

while True:
    # Check distance condition
    distance_traveled = robot.odom.pose.x - start_x
    if distance_traveled >= target_distance:
        print("Reached target distance!")
        break

    # Future: Check sensor condition
    # if robot.lidar.front < 30:  # Wall within 30cm
    #     print("Wall detected!")
    #     break

    # Keep moving
    robot.drive.forward(0.2)
    time.sleep(0.01)

robot.drive.halt()
```

**This is where user-written loops shine** - multiple stopping conditions!

---

### Example 5: Move Until Position AND Angle Reached

Move to `(x=1.0, y=0.5)` and face North (θ=π/2):

```python
import time
import math

target_x = 1.0
target_y = 0.5
target_theta = math.pi / 2  # 90° (North)

while True:
    # Calculate errors
    error_x = target_x - robot.odom.pose.x
    error_y = target_y - robot.odom.pose.y
    error_theta = target_theta - robot.odom.pose.theta

    # Normalize angle
    while error_theta > math.pi:
        error_theta -= 2 * math.pi
    while error_theta < -math.pi:
        error_theta += 2 * math.pi

    # Check if all close enough
    pos_error = math.sqrt(error_x**2 + error_y**2)
    if pos_error < 0.02 and abs(error_theta) < 0.05:
        break

    # Proportional control for all three
    # Note: error_x/error_y are in WORLD frame, need to transform to robot frame!
    current_theta = robot.odom.pose.theta

    # Transform world frame errors to robot frame
    cos_t = math.cos(current_theta)
    sin_t = math.sin(current_theta)
    error_x_robot = error_x * cos_t + error_y * sin_t
    error_y_robot = -error_x * sin_t + error_y * cos_t

    K_linear = 0.4
    K_rotation = 0.6

    vx = K_linear * error_x_robot
    vy = K_linear * error_y_robot
    vtheta = K_rotation * error_theta

    # Limit speeds
    vx = max(-0.3, min(0.3, vx))
    vy = max(-0.3, min(0.3, vy))
    vtheta = max(-0.5, min(0.5, vtheta))

    robot.drive.move(vx=vx, vy=vy, vtheta=vtheta)

    time.sleep(0.01)

robot.drive.halt()
print(f"Arrived at ({robot.odom.pose.x:.3f}, {robot.odom.pose.y:.3f}), θ={math.degrees(robot.odom.pose.theta):.1f}°")
```

**This is advanced!** You're controlling 3 things simultaneously using proportional control.

---

## What's Next: Adding More Sensors

Right now, you can make decisions based on **odometry** (where the robot is). But what if you could also sense:

- **Walls and obstacles** - using lidar
- **Colors and objects** - using camera
- **Distance to specific targets** - using depth camera

That's what Chapter 6 is about!

### Preview: Sensor-Based Control

**Imagine:**
```python
# Move forward until you see a wall
while robot.lidar.front > 30:  # More than 30cm clearance
    robot.drive.forward(0.2)
    time.sleep(0.01)

robot.drive.halt()
print("Wall detected!")
```

Or:
```python
# Move toward red object
while True:
    if robot.camera.red_detected:
        # Move toward red
        robot.drive.forward(0.2)
    else:
        # Spin to find red
        robot.drive.rotate_ccw(0.3)

    time.sleep(0.01)
```

**You already know how to write these loops!** Chapter 6 just adds more sensors to check.

---

## Summary

In this chapter you learned:

✅ **Reading Odometry:**
- Access position: `robot.odom.pose.x/y/theta`
- Access velocity: `robot.odom.velocity.vx/vy/vtheta`
- Real-time monitoring while moving

✅ **Writing Control Loops:**
- Simple while loop with condition checking
- When to check and when to stop
- Combining movement with decision logic

✅ **Proportional Control:**
- Speed proportional to distance remaining
- Smooth approach to target
- Speed limiting (min/max)

✅ **Decision Guide:**
- Use built-in methods for simple movements
- Write loops for custom logic and sensor checking
- Each approach has its strengths

✅ **Practical Examples:**
- Move to world position
- Rotate to specific angle
- Circle around origin
- Multiple stopping conditions
- Advanced 3-DOF control

**Key Insight:** The robot doesn't "think" for you - YOU read sensors, make decisions, and command movements. This is the foundation of robotics programming!

---

### What's Next?

**Chapter 6: Sensors (Lidar & Camera)**

Now that you can write control loops, let's add more sensors!

- RPLidar C1 for obstacle detection
- Orbbec Camera for vision
- Combining odometry + sensors for smarter behavior
- **Lessons 4.1-4.5**: Lidar-based behaviors
- **Lessons 5.1-5.5**: Camera-based behaviors

You'll use the SAME control loop patterns from this chapter, just checking different sensors!

---

**Ready to add eyes to your robot?** → Chapter 6

Have fun! 🤖
