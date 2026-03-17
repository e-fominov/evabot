# Chapter 7: Maze Challenge

**Add a camera, drop a payload, escape dead ends, and find the finish!**

In Chapter 6, you built a maze explorer that visits cells one by one. But it got stuck in dead ends and couldn't detect anything on the floor. Now you'll add a camera to see colors, a dropper motor to deliver a payload, and backtracking to escape dead ends.

---

## What You'll Learn

1. Use the camera to detect floor colors
2. React to colors (blue = drop zone, red = finish)
3. Control a dropper motor to release a payload
4. Understand why dead ends are a problem
5. Add backtracking with a path stack
6. Build a complete maze challenge robot

---

## The Camera

The camera looks at the floor and can detect colors. It works differently from the lidar — instead of measuring distance, it tells you what color it sees.

### Reading Colors

```python
import time
from evabot.components.sensors import Camera

camera = Camera()
camera.start()

time.sleep(2)

# Get the color as HSV (Hue, Saturation, Value)
hsv = camera.get_color()
if hsv:
    h, s, v = hsv
    print(f"Hue: {h}, Saturation: {s}, Value: {v}")

camera.stop()
```

HSV is a way to describe color:
- **Hue** (0-179): The actual color (red=0, yellow=30, green=60, blue=120)
- **Saturation** (0-255): How vivid the color is (0=gray, 255=pure color)
- **Value** (0-255): How bright (0=dark, 255=bright)

### Matching Named Colors

Instead of reading raw HSV, you can ask "is this blue?"

```python
score = camera.match_color("blue")
print(f"Blue confidence: {score:.2f}")
```

`match_color()` returns a confidence score from 0.0 to 1.0:
- **0.0** = definitely not that color
- **0.05+** = likely that color
- **1.0** = entire view is that color

Available colors: `"red"`, `"yellow"`, `"green"`, `"blue"`, `"white"`, `"black"`

### Color Scanner

```python
import time
from evabot.components.sensors import Camera

camera = Camera()
camera.start()

time.sleep(2)

COLORS = ["red", "yellow", "green", "blue", "white", "black"]

# Scan 10 times
for i in range(10):
    scores = {c: camera.match_color(c) for c in COLORS}
    best = max(scores, key=scores.get)
    conf = scores[best]

    if conf > 0.05:
        print(f"I see: {best} (confidence: {conf:.2f})")
    else:
        print("No clear color")

    time.sleep(0.5)

camera.stop()
```

**Try it:** Place colored paper under the robot and run the code. Move different colors underneath to see it detect them.

---

### Exercise 7.1: Color Alarm

Print "ALERT!" when the camera sees red. Print "OK" for any other color.

<details>
<summary>Solution</summary>

```python
import time
from evabot.components.sensors import Camera

camera = Camera()
camera.start()

time.sleep(2)

for i in range(20):
    if camera.match_color("red") > 0.05:
        print("ALERT! Red detected!")
    else:
        print("OK")
    time.sleep(0.5)

camera.stop()
```

</details>

---

## The Dropper Motor

The dropper is a regular motor (Servo42D) on CAN ID 5. Spinning it opens a mechanism that releases a payload (like a ball or small object).

### Simple Drop

```python
import time
from evabot import Servo42D

dropper = Servo42D(5)
dropper.start()

# Spin to release payload
dropper.run(30)       # 30 RPM
time.sleep(1.0)       # for 1 second
dropper.run(0)        # stop

dropper.stop()
```

That's it! Spin the motor, wait, stop. The mechanical design does the rest.

---

### Exercise 7.2: Drop on Blue

Combine camera and dropper: when blue is detected, drop the payload.

<details>
<summary>Solution</summary>

```python
import time
from evabot import Servo42D
from evabot.components.sensors import Camera

camera = Camera()
camera.start()

dropper = Servo42D(5)
dropper.start()

time.sleep(2)

print("Waiting for blue...")
while True:
    if camera.match_color("blue") > 0.05:
        print("Blue detected! Dropping payload...")
        dropper.run(30)
        time.sleep(1.0)
        dropper.run(0)
        print("Dropped!")
        break
    time.sleep(0.3)

dropper.stop()
camera.stop()
```

</details>

---

## Adding Camera to the Maze Explorer

Now let's add color detection to our maze explorer from Chapter 6. After each move, the robot checks the floor:

- **Blue** = drop zone → release payload
- **Red** = finish line → stop exploring

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1, Servo42D
from evabot.components.sensors import Camera

robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1()
robot.start()

camera = Camera()
camera.start()

dropper = Servo42D(5)
dropper.start()

payload_dropped = False

time.sleep(3)

# ... after each move_to_wall() in the exploration loop:

# Check for finish
if camera.match_color("red") > 0.05:
    print("RED ZONE - FINISH!")
    break

# Check for drop zone
if not payload_dropped:
    if camera.match_color("blue") > 0.05:
        print("BLUE ZONE! Dropping payload...")
        dropper.run(30)
        time.sleep(1.0)
        dropper.run(0)
        payload_dropped = True
```

**Key details:**
- Check red first (finish is more important than dropping)
- `payload_dropped` flag ensures we only drop once
- The checks happen after each cell move, while the robot is stopped

---

## The Dead End Problem

Our Chapter 6 explorer has a big problem. Look at this maze:

```
+---+---+---+---+
|               |
+   +---+---+   +
|   |       |   |
+   +   +   +   +
|       |   |   |
+---+---+---+---+
```

The robot starts bottom-left and goes left, left, left... hits the end. All neighbors are visited. **It stops, even though the right side is unexplored!**

```
Step 1: (0,0) → go left
Step 2: (0,1) → go left
Step 3: (0,2) → go left
Step 4: (0,3) → STUCK! All neighbors visited.
         But (1,0), (2,0), etc. are still unexplored!
```

---

## Backtracking with a Path Stack

The fix is simple: **remember the path you took, and walk it backwards when stuck.**

### How It Works

Think of leaving breadcrumbs as you walk:

```
Forward:   (0,0) →left→ (0,1) →left→ (0,2) →left→ (0,3) → stuck!
           [push]        [push]        [push]

Backtrack: (0,3) →right→ (0,2) → has unvisited neighbor? No.
           [pop]
           (0,2) →right→ (0,1) → has unvisited neighbor? No.
           [pop]
           (0,1) →right→ (0,0) → has unvisited neighbor? YES!
           [pop]

Continue:  (0,0) →front→ (1,0) → new territory!
           [push]
```

### The Path Stack

A **stack** is a list where you always add and remove from the end (like a stack of plates — last in, first out).

```python
path = []

# Going forward: push where we came from
path.append((cell_x, cell_y, direction))

# Going backward: pop and reverse the direction
prev_x, prev_y, came_from = path.pop()
back_direction = OPPOSITE[came_from]
```

Each entry in the stack stores:
- `cell_x, cell_y` — the cell we were in before moving
- `direction` — which way we went

To backtrack, we pop the entry and move in the **opposite** direction.

---

### Exercise 7.3: Understand the Stack

Given this maze and path, what does the stack look like after 4 moves?

```
+---+---+---+
|       |   |
+---+   +   +
|   |       |
+---+---+---+

Start at (0,0), priority: left, back, right, front
```

<details>
<summary>Solution</summary>

```
Step 1: At (0,0), go front to (1,0)  → stack: [(0,0,front)]
Step 2: At (1,0), go left to (1,1)   → stack: [(0,0,front), (1,0,left)]
Step 3: At (1,1), go front to (2,1)  → stack: [(0,0,front), (1,0,left), (1,1,front)]
Step 4: At (2,1), go right to (2,0)  → stack: [(0,0,front), (1,0,left), (1,1,front), (2,1,right)]
```

If stuck at (2,0), pop (2,1,right) → go left (opposite of right) back to (2,1).

</details>

---

## The Backtracking Loop

Here's how the exploration loop changes:

```python
path = []  # stack for backtracking

for step in range(200):
    # Scan and update map (same as before)
    visited.add((cell_x, cell_y))
    # ... scan walls, record them ...

    # Find unvisited neighbor
    neighbors = get_unvisited_neighbors(cell_x, cell_y)

    if neighbors:
        # Forward: go to new cell, push to stack
        direction, nx, ny = neighbors[0]
        path.append((cell_x, cell_y, direction))
        robot.move_to_wall(direction, max_travel=0.30)
        cell_x, cell_y = nx, ny

    elif path:
        # Dead end: backtrack until we find unexplored path
        print("Dead end, backtracking...")
        while path:
            prev_x, prev_y, came_from = path.pop()
            back_dir = OPPOSITE[came_from]
            robot.move_to_wall(back_dir, max_travel=0.30)
            cell_x, cell_y = prev_x, prev_y

            if get_unvisited_neighbors(cell_x, cell_y):
                break  # found a cell with unexplored neighbors!
        else:
            break  # backtracked to start, maze fully explored

        continue  # go back to top of loop to scan and move forward

    else:
        break  # no neighbors, no path — done
```

**Three cases:**
1. **Has unvisited neighbor** → go there (push to stack)
2. **No unvisited neighbor, but path exists** → backtrack (pop from stack)
3. **No neighbor, no path** → fully explored

---

## The Complete Maze Challenge

Putting it all together: camera, dropper, backtracking, and the maze explorer.

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1, Servo42D
from evabot.components.sensors import Camera

# Setup
robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1(max_range=1.0)
robot.start()

camera = Camera()
camera.start()

dropper = Servo42D(5)
dropper.start()

time.sleep(3)
print("Press ENTER to start!")
input()

# Direction helpers
DIR_DELTA = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}
OPPOSITE = {0: 180, 180: 0, 90: 270, 270: 90}
DIR_NAMES = {0: "Front", 90: "Right", 180: "Back", 270: "Left"}
WALL_THRESHOLD = 0.25

# Map
visited = set()
walls = {}
path = []
payload_dropped = False

def set_wall(x, y, d, has_wall):
    walls[(x, y, d)] = has_wall
    dx, dy = DIR_DELTA[d]
    walls[(x + dx, y + dy, OPPOSITE[d])] = has_wall

# Start
x, y = 0, 0

for step in range(200):
    print(f"\n--- Cell ({x},{y}) Step {step+1} ---")

    # Scan walls
    visited.add((x, y))
    for angle in [0, 90, 180, 270]:
        dist, _, q = robot.lidar.check_wall(angle)
        has_wall = dist is not None and q is not None and q > 0.3 and dist < WALL_THRESHOLD
        set_wall(x, y, angle, has_wall)

    # Find unvisited neighbor (priority: left, back, right, front)
    neighbors = []
    for d in [270, 180, 90, 0]:
        dx, dy = DIR_DELTA[d]
        nx, ny = x + dx, y + dy
        if walls.get((x, y, d)) is False and (nx, ny) not in visited:
            neighbors.append((d, nx, ny))

    if neighbors:
        direction, nx, ny = neighbors[0]
        print(f"  Moving {DIR_NAMES[direction]} -> ({nx},{ny})")
        path.append((x, y, direction))
        robot.move_to_wall(direction, max_travel=0.30)
        x, y = nx, ny

    elif path:
        print("  Backtracking...")
        while path:
            px, py, came_from = path.pop()
            robot.move_to_wall(OPPOSITE[came_from], max_travel=0.30)
            x, y = px, py
            # Check if this cell has unexplored neighbors
            for d in [270, 180, 90, 0]:
                dx, dy = DIR_DELTA[d]
                nx, ny = x + dx, y + dy
                if walls.get((x, y, d)) is False and (nx, ny) not in visited:
                    print(f"  Found path at ({x},{y})")
                    break
            else:
                continue  # no neighbors here, keep backtracking
            break  # found neighbors, stop backtracking
        else:
            print("  Fully explored!")
            break
        continue

    else:
        print("  Fully explored!")
        break

    # Check colors
    if camera.match_color("red") > 0.05:
        print("  RED - FINISH!")
        break

    if not payload_dropped and camera.match_color("blue") > 0.05:
        print("  BLUE - Dropping payload!")
        dropper.run(30)
        time.sleep(1.0)
        dropper.run(0)
        payload_dropped = True

print(f"\nVisited {len(visited)} cells!")
robot.drive.halt()
dropper.stop()
camera.stop()
robot.stop()
```

---

### Exercise 7.4: Count Backtracks

Add a counter that tracks how many times the robot backtracks. Print it at the end.

<details>
<summary>Solution</summary>

```python
# Add before the loop:
backtrack_count = 0

# In the backtrack section, after "Backtracking...":
backtrack_count += 1

# At the end:
print(f"Backtracked {backtrack_count} times")
```

</details>

---

### Exercise 7.5: Speed Boost on Backtrack

When backtracking, the robot already knows the path is safe. Make it move faster during backtracking (speed=0.5) and slower during exploration (speed=0.3).

<details>
<summary>Solution</summary>

```python
# Forward movement:
robot.move_to_wall(direction, speed=0.3, max_travel=0.30)

# Backtrack movement:
robot.move_to_wall(OPPOSITE[came_from], speed=0.5, max_travel=0.30)
```

The robot already visited these cells, so it knows there are no surprises. Faster backtracking means less wasted time in dead ends!

</details>

---

## How It All Fits Together

```
┌─────────────────────────────────┐
│         SCAN WALLS              │
│   check_wall() × 4 directions  │
└───────────────┬─────────────────┘
                │
        ┌───────▼───────┐
        │  Has unvisited │──── YES ──→ PUSH to stack
        │   neighbor?    │             move_to_wall()
        └───────┬────────┘             check colors
                │ NO                        │
        ┌───────▼───────┐                   │
        │  Path stack    │──── YES ──→ POP from stack
        │   not empty?   │             move_to_wall(OPPOSITE)
        └───────┬────────┘             has neighbors? ──→ loop back
                │ NO                                 NO → keep popping
                │
            DONE! ◄─────────────────────────────────┘
```

The robot will always explore every reachable cell. It might visit some cells twice (during backtracking), but it will never miss a cell and never go in circles.

---

## Summary

You learned:

- Read floor colors with `camera.get_color()` and `camera.match_color()`
- React to specific colors (blue = drop, red = finish)
- Control a dropper motor with `Servo42D(5).run(speed)`
- Why dead ends break simple exploration
- Backtracking with a path stack (DFS)
- Push when going forward, pop when stuck
- The complete maze challenge: explore, detect colors, deliver payload, find finish

**The maze challenge robot in one sentence:**
> Scan walls, pick an unvisited neighbor, move there, check colors, and when stuck — backtrack until you find a new path.

---

## What's Next?

Congratulations! You've built a robot that can:
- Drive precisely with mecanum wheels
- Sense walls with lidar
- See colors with a camera
- Navigate a maze from start to finish
- Deliver a payload at the right spot

Ideas to explore further:
- **Shortest path** — After exploring, find the fastest route from start to finish
- **Speed optimization** — How fast can you complete the maze?
- **Multiple payloads** — Drop different items at different colored zones
- **Maze mapping** — Display the complete maze map after exploration
