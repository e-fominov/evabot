# Chapter 5: Wall Following and Navigation

**Learn to align with walls and navigate around a room**

In Chapter 4, you learned to stop before a wall. Now you'll learn to align parallel to walls and navigate around a room.

---

## What You'll Learn

1. Measure if robot is parallel to a wall (two-point method)
2. Align parallel to a wall by rotating
3. Drive while maintaining alignment
4. Use `check_wall()` for easier alignment
5. Use `get_clearance()` for safer obstacle detection
6. Navigate around a square room

---

## Two-Point Alignment Check

To know if you're parallel to a wall, measure distance at two angles.

### How It Works

If you measure distance at two nearby angles and they're the same, you're parallel!

```
  Robot parallel to wall:        Robot angled to wall:

  -------- WALL --------         -------- WALL --------
      |           |                  |       |
      20cm       20cm                15cm    25cm
      |           |                  |       |
      ●-----------                   ●-------
     ROBOT                          ROBOT (angled)
```

**Idea:** Measure at angles 80° and 100° (20° apart). If distances are different, robot is angled.

### Simple Alignment Check

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Measure two points on the right side
d1 = robot.lidar.get_distance_at_angle(80)
d2 = robot.lidar.get_distance_at_angle(100)

if d1 and d2:
    diff = d1 - d2
    print(f"Distance at 80°: {d1:.2f}m")
    print(f"Distance at 100°: {d2:.2f}m")
    print(f"Difference: {diff:.2f}m")

    if abs(diff) < 0.02:  # Less than 2cm difference
        print("Parallel to wall!")
    else:
        print("Not parallel - need to rotate")

robot.stop()
```

**How to read the difference:**
- `diff > 0`: Front closer to wall, need to rotate CW (clockwise)
- `diff < 0`: Back closer to wall, need to rotate CCW (counter-clockwise)
- `diff ≈ 0`: Parallel!

---

## Aligning to a Wall

Now let's rotate until we're parallel.

### Align by Rotating

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Rotate until parallel to right wall
while True:
    d1 = robot.lidar.get_distance_at_angle(80)
    d2 = robot.lidar.get_distance_at_angle(100)

    if d1 and d2:
        diff = d1 - d2

        if abs(diff) < 0.02:  # Parallel!
            break

        # Rotate to align
        if diff > 0:
            robot.drive.move(vtheta=-0.2)  # Rotate CW
        else:
            robot.drive.move(vtheta=0.2)   # Rotate CCW

    time.sleep(0.1)

robot.drive.halt()
robot.stop()
```

**How it works:**
1. Measure two points
2. Calculate difference
3. If not parallel, rotate in correct direction
4. Repeat until parallel

---

### Exercise 5.1: Align to Front Wall

Write code to align parallel to the front wall (use angles 350° and 10°).

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

while True:
    d1 = robot.lidar.get_distance_at_angle(350)
    d2 = robot.lidar.get_distance_at_angle(10)

    if d1 and d2:
        diff = d1 - d2

        if abs(diff) < 0.02:
            break

        if diff > 0:
            robot.drive.move(vtheta=-0.2)
        else:
            robot.drive.move(vtheta=0.2)

    time.sleep(0.1)

robot.drive.halt()
robot.stop()
```

</details>

---

## Driving While Aligned

Now let's drive forward while keeping parallel to a wall.

### Drive and Align Loop

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Drive forward for 3 seconds while staying aligned to right wall
start_time = time.time()

while time.time() - start_time < 3.0:
    # Check alignment
    d1 = robot.lidar.get_distance_at_angle(80)
    d2 = robot.lidar.get_distance_at_angle(100)

    if d1 and d2:
        diff = d1 - d2

        # Adjust rotation to stay aligned
        if abs(diff) < 0.02:
            vtheta = 0  # Parallel, no rotation
        elif diff > 0:
            vtheta = -0.1  # Small CW rotation
        else:
            vtheta = 0.1   # Small CCW rotation

        # Drive forward with alignment correction
        robot.drive.move(vx=0.1, vtheta=vtheta)

    time.sleep(0.1)

robot.drive.halt()
robot.stop()
```

**How it works:**
1. Measure alignment while moving
2. If not parallel, add small rotation
3. Continue driving forward with rotation correction
4. Result: robot drives straight while staying parallel!

---

### Exercise 5.2: Strafe While Aligned

Modify the code to strafe left while staying aligned to the front wall.

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

start_time = time.time()

while time.time() - start_time < 3.0:
    d1 = robot.lidar.get_distance_at_angle(350)
    d2 = robot.lidar.get_distance_at_angle(10)

    if d1 and d2:
        diff = d1 - d2

        if abs(diff) < 0.02:
            vtheta = 0
        elif diff > 0:
            vtheta = -0.1
        else:
            vtheta = 0.1

        robot.drive.move(vy=0.1, vtheta=vtheta)

    time.sleep(0.1)

robot.drive.halt()
robot.stop()
```

</details>

---

## Using check_wall()

Calculating alignment manually works, but there's an easier way!

### The check_wall() Function

```python
distance, angle_deg, quality = robot.lidar.check_wall(90)
```

**Returns:**
- `distance`: Perpendicular distance to wall (meters)
- `angle_deg`: How much you need to rotate to be parallel (degrees)
  - Positive = rotate CW to align
  - Negative = rotate CCW to align
- `quality`: How good the measurement is (0-1, higher is better)

### Simple Alignment with check_wall()

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Align to right wall
while True:
    distance, angle_deg, quality = robot.lidar.check_wall(90)

    if angle_deg is not None:
        if abs(angle_deg) < 2.0:  # Within 2 degrees
            break

        # Rotate proportionally to error
        vtheta = 0.02 * angle_deg  # Positive angle = rotate CW
        robot.drive.move(vtheta=vtheta)

    time.sleep(0.1)

robot.drive.halt()
robot.stop()
```

**Much simpler!** No need to measure two points or calculate difference.

---

### Exercise 5.3: Align to Front Wall with check_wall()

Use `check_wall()` to align to the front wall (angle 0).

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

while True:
    distance, angle_deg, quality = robot.lidar.check_wall(0)

    if angle_deg is not None:
        if abs(angle_deg) < 2.0:
            break

        vtheta = 0.02 * angle_deg
        robot.drive.move(vtheta=vtheta)

    time.sleep(0.1)

robot.drive.halt()
robot.stop()
```

</details>

---

## Using get_clearance()

When checking distance to a wall, `get_clearance()` is safer than `get_distance_at_angle()`.

### Why get_clearance() is Better

```python
# get_distance_at_angle() - measures at ONE angle
distance = robot.lidar.get_distance_at_angle(0)

# get_clearance() - looks at a RANGE of angles
distance = robot.lidar.get_clearance(angle=0, robot_width=0.22, angular_range=30)
```

**Benefits:**
- Checks multiple angles (safer - won't miss obstacles)
- Accounts for robot width
- Returns closest obstacle in the area

### Approaching Wall with get_clearance()

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Move forward until 20cm from wall
robot.drive.move(vx=0.1)

while True:
    clearance = robot.lidar.get_clearance(angle=0, robot_width=0.22)

    if clearance and clearance < 0.20:
        break

    time.sleep(0.05)

robot.drive.halt()
robot.stop()
```

---

## Wall Following

Now combine everything: approach a wall, align, then strafe along it.

### Approach, Align, and Follow

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Step 1: Approach front wall
robot.drive.move(vx=0.1)
while True:
    clearance = robot.lidar.get_clearance(0, 0.22)
    if clearance and clearance < 0.20:
        break
    time.sleep(0.05)
robot.drive.halt()
time.sleep(0.5)

# Step 2: Align to front wall
while True:
    distance, angle_deg, quality = robot.lidar.check_wall(0)
    if angle_deg and abs(angle_deg) < 2.0:
        break
    if angle_deg:
        robot.drive.move(vtheta=0.02 * angle_deg)
    time.sleep(0.1)
robot.drive.halt()
time.sleep(0.5)

# Step 3: Strafe left while maintaining alignment
start_time = time.time()
while time.time() - start_time < 3.0:
    # Check left wall
    left_clear = robot.lidar.get_clearance(270, 0.22)
    if left_clear and left_clear < 0.20:
        break

    # Maintain alignment to front wall
    distance, angle_deg, quality = robot.lidar.check_wall(0)
    vtheta = 0.02 * angle_deg if angle_deg else 0

    robot.drive.move(vy=0.1, vtheta=vtheta)
    time.sleep(0.1)

robot.drive.halt()
robot.stop()
```

**What this does:**
1. Moves forward to front wall
2. Rotates to align parallel
3. Strafes left while staying parallel to front wall
4. Stops when reaching left wall

---

## Square Navigation

Now let's navigate around a square room!

### Navigate Around the Room

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern='X')
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Walls: 0=front, 90=right, 180=back, 270=left
walls = [
    (0, 'vx', 0.1),    # Approach front wall
    (270, 'vy', 0.1),  # Strafe to left wall (following front)
    (180, 'vx', -0.1), # Move to back wall (following left)
    (90, 'vy', -0.1),  # Strafe to right wall (following back)
]

for i, (target_wall, move_dir, speed) in enumerate(walls):
    # Determine which wall to follow
    if i == 0:
        follow_wall = None  # First move, just approach
    else:
        follow_wall = walls[i-1][0]  # Follow previous wall

    print(f"Moving to wall {target_wall}")

    # Move until reaching target wall
    while True:
        clearance = robot.lidar.get_clearance(target_wall, 0.22)
        if clearance and clearance < 0.20:
            break

        # Maintain alignment to follow_wall if exists
        vtheta = 0
        if follow_wall is not None:
            dist, angle_deg, quality = robot.lidar.check_wall(follow_wall)
            if angle_deg:
                vtheta = 0.02 * angle_deg

        # Move toward target
        if move_dir == 'vx':
            robot.drive.move(vx=speed, vtheta=vtheta)
        else:
            robot.drive.move(vy=speed, vtheta=vtheta)

        time.sleep(0.1)

    robot.drive.halt()
    time.sleep(0.5)

    # Align to target wall
    print(f"Aligning to wall {target_wall}")
    while True:
        dist, angle_deg, quality = robot.lidar.check_wall(target_wall)
        if angle_deg and abs(angle_deg) < 2.0:
            break
        if angle_deg:
            robot.drive.move(vtheta=0.02 * angle_deg)
        time.sleep(0.1)

    robot.drive.halt()
    time.sleep(0.5)

print("Square complete!")
robot.stop()
```

**What this does:**
1. Move to front wall → align
2. Strafe left (following front wall) → reach left wall → align
3. Move backward (following left wall) → reach back wall → align
4. Strafe right (following back wall) → reach right wall → align
5. Robot has navigated the perimeter!

---

### Exercise 5.4: Return to Start

After completing the square, add one more move to return to the front wall (completing the loop).

<details>
<summary>Solution</summary>

```python
# Add this after the loop above:

print("Returning to front wall")

# Move forward following right wall
while True:
    clearance = robot.lidar.get_clearance(0, 0.22)
    if clearance and clearance < 0.20:
        break

    dist, angle_deg, quality = robot.lidar.check_wall(90)
    vtheta = 0.02 * angle_deg if angle_deg else 0

    robot.drive.move(vx=0.1, vtheta=vtheta)
    time.sleep(0.1)

robot.drive.halt()
print("Back at start!")
robot.stop()
```

</details>

---

## Summary

You learned:

✅ Manual two-point alignment check
✅ Rotate to align parallel to walls
✅ Drive while maintaining alignment
✅ Use `check_wall()` for easy alignment
  - Returns distance, angle error, and quality
  - Positive angle = rotate CW, negative = rotate CCW
✅ Use `get_clearance()` for safe obstacle detection
  - Checks range of angles, not just one point
  - Accounts for robot width
✅ Wall following (approach → align → follow)
✅ Square navigation around a room

**Key pattern for wall following:**
```python
# Move toward wall
robot.drive.move(vx=0.1, vtheta=alignment_correction)

while True:
    # Check distance to target wall
    clearance = robot.lidar.get_clearance(target_angle, 0.22)
    if clearance < 0.20:
        break

    # Maintain alignment to follow_wall
    dist, angle_deg, quality = robot.lidar.check_wall(follow_angle)
    vtheta = 0.02 * angle_deg if angle_deg else 0

    robot.drive.move(vx=speed, vtheta=vtheta)
    time.sleep(0.1)

robot.drive.halt()
```

---

## What's Next?

Chapter 6 will teach you maze solving:
- Detect corners and openings
- Make navigation decisions
- Follow left-wall or right-wall strategy
- Find the exit!

Ready for the maze? 🤖
