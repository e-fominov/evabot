# Chapter 6: Maze Explorer

**Teach your robot to navigate a maze**

In Chapter 5, you learned to follow walls and navigate around a room. Now you'll put it all together to explore a maze!

---

## What You'll Learn

1. How maze cells work (walls and openings)
2. Detect which walls are open
3. Use `move_to_wall()` for safe cell-to-cell movement
4. Keep a map of visited cells
5. Choose where to go next
6. Build a complete maze explorer

---

## How Mazes Work

A maze is made of **cells** - small rooms with some walls open.

```
+---+---+---+
|           |
+---+   +---+
|   |       |
+---+   +---+
|       |   |
+---+---+---+
```

Each cell has 4 sides: front, right, back, left. Some sides have walls, some are open.

**Your robot starts in one cell and needs to visit every cell.**

The robot knows:
- Which walls are around it (lidar)
- Which cells it already visited (memory)

It doesn't know:
- What the maze looks like ahead
- How big the maze is

---

## Detecting Walls

The lidar can detect walls in any direction using `check_wall()`:

```python
distance, angle, quality = robot.lidar.check_wall(0)    # front
distance, angle, quality = robot.lidar.check_wall(90)   # right
distance, angle, quality = robot.lidar.check_wall(180)  # back
distance, angle, quality = robot.lidar.check_wall(270)  # left
```

In a 30cm maze cell, a wall is about 12-15cm away. An opening is much farther (30cm+).

### Scan All Four Walls

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Check all 4 directions
for name, angle in [('Front', 0), ('Right', 90), ('Back', 180), ('Left', 270)]:
    dist, _, quality = robot.lidar.check_wall(angle)

    if dist is not None and quality > 0.3 and dist < 0.25:
        print(f"{name}: WALL at {dist*100:.1f}cm")
    else:
        print(f"{name}: OPEN")

robot.stop()
```

**Try it:** Place the robot in a maze cell and run the code. It should show 3 walls and 1 opening (or however your cell is set up).

---

## Moving Between Cells with move_to_wall()

Moving blindly is dangerous - the robot might crash into walls. Instead, use `move_to_wall()` which uses lidar to move safely:

```python
robot.move_to_wall(0)    # move forward to next wall
robot.move_to_wall(270)  # move left to next wall
robot.move_to_wall(90)   # move right to next wall
robot.move_to_wall(180)  # move backward to next wall
```

### What move_to_wall() Does

While moving, it continuously:
1. **Watches the wall ahead** - stops when close enough
2. **Pushes away from side walls** - keeps centered in the corridor
3. **Aligns to walls** - keeps the robot straight

```
    WALL
    ════════════════
         ↑ push away
    ┌───┐
    │ R │ ──────→ moving right
    └───┘
         ↓ push away
    ════════════════
    WALL
```

### Moving Through an Opening

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Find which direction is open
for name, angle in [('Front', 0), ('Right', 90), ('Back', 180), ('Left', 270)]:
    dist, _, q = robot.lidar.check_wall(angle)
    if dist is None or q is None or q < 0.3 or dist > 0.25:
        print(f"{name} is open! Moving there...")
        robot.move_to_wall(angle)
        break

robot.drive.halt()
robot.stop()
```

**What happens:** The robot finds the opening, moves through it, and stops in the next cell when it sees a wall ahead.

---

### Exercise 6.1: Move and Scan

Move through the opening, then scan walls in the new cell. Print what you find.

<details>
<summary>Solution</summary>

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Find opening and move through it
for name, angle in [('Front', 0), ('Right', 90), ('Back', 180), ('Left', 270)]:
    dist, _, q = robot.lidar.check_wall(angle)
    if dist is None or q is None or q < 0.3 or dist > 0.25:
        print(f"Moving {name}...")
        robot.move_to_wall(angle)
        break

time.sleep(0.5)

# Scan new cell
print("New cell:")
for name, angle in [('Front', 0), ('Right', 90), ('Back', 180), ('Left', 270)]:
    dist, _, q = robot.lidar.check_wall(angle)
    if dist is not None and q is not None and q > 0.3 and dist < 0.25:
        print(f"  {name}: WALL at {dist*100:.1f}cm")
    else:
        print(f"  {name}: OPEN")

robot.drive.halt()
robot.stop()
```

</details>

---

## Remembering Where You've Been

To explore a maze, the robot needs to remember:
- **Which cells it visited** (so it doesn't go in circles)
- **Where walls are** (so it knows which cells are connected)

We use simple Python data structures:

```python
# Track visited cells as (x, y) coordinates
visited = set()

# Track walls: (x, y, direction) -> True/False
walls = {}
```

The robot starts at cell `(0, 0)`. When it moves:
- **Front (0):** x increases → `(1, 0)`
- **Back (180):** x decreases → `(-1, 0)`
- **Left (270):** y increases → `(0, 1)`
- **Right (90):** y decreases → `(0, -1)`

```
         Front (+x)
           ↑
  Left ← (0,0) → Right
  (+y)     ↓      (-y)
         Back (-x)
```

### Recording Walls

```python
# Direction to coordinate change
DIR_DELTA = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}
OPPOSITE = {0: 180, 180: 0, 90: 270, 270: 90}

visited = set()
walls = {}

def set_wall(x, y, direction, has_wall):
    """Record a wall (also records it from the neighbor's side)."""
    walls[(x, y, direction)] = has_wall
    # The neighbor sees the same wall from the opposite direction
    dx, dy = DIR_DELTA[direction]
    walls[(x + dx, y + dy, OPPOSITE[direction])] = has_wall
```

**Why record from both sides?** If cell (0,0) has a wall on the right, then cell (0,-1) has a wall on the left. Recording both means we always know about walls even before visiting a cell.

---

## Choosing Where to Go

The simplest strategy: **visit any unvisited neighbor**.

```python
EXPLORE_PRIORITY = [270, 180, 90, 0]  # left, back, right, front

def get_next_cell(x, y):
    """Find an unvisited neighbor with no wall blocking it."""
    for direction in EXPLORE_PRIORITY:
        dx, dy = DIR_DELTA[direction]
        nx, ny = x + dx, y + dy

        # Check: is there a wall blocking this direction?
        has_wall = walls.get((x, y, direction))

        # If no wall AND not visited → go there!
        if has_wall is False and (nx, ny) not in visited:
            return direction, nx, ny

    return None  # No unvisited neighbors
```

**Priority order** decides which direction the robot prefers. Left-first tends to explore methodically (like following the left wall).

---

### Exercise 6.2: Two Cells

Scan the first cell, move to an unvisited neighbor, scan the second cell.

<details>
<summary>Solution</summary>

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

DIR_DELTA = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}
OPPOSITE = {0: 180, 180: 0, 90: 270, 270: 90}
visited = set()
walls = {}

def set_wall(x, y, direction, has_wall):
    walls[(x, y, direction)] = has_wall
    dx, dy = DIR_DELTA[direction]
    walls[(x + dx, y + dy, OPPOSITE[direction])] = has_wall

# Start at (0, 0)
x, y = 0, 0

for cell_num in range(2):
    print(f"\nCell ({x}, {y}):")
    visited.add((x, y))

    # Scan all walls
    for name, angle in [('Front', 0), ('Right', 90), ('Back', 180), ('Left', 270)]:
        dist, _, q = robot.lidar.check_wall(angle)
        has_wall = dist is not None and q is not None and q > 0.3 and dist < 0.25
        set_wall(x, y, angle, has_wall)
        print(f"  {name}: {'WALL' if has_wall else 'OPEN'}")

    # Find unvisited neighbor
    for direction in [270, 180, 90, 0]:  # left, back, right, front
        dx, dy = DIR_DELTA[direction]
        nx, ny = x + dx, y + dy
        if walls.get((x, y, direction)) is False and (nx, ny) not in visited:
            dir_name = {0: 'Front', 90: 'Right', 180: 'Back', 270: 'Left'}[direction]
            print(f"  Moving {dir_name} to ({nx}, {ny})")
            robot.move_to_wall(direction, max_travel=0.30)
            x, y = nx, ny
            break

robot.drive.halt()
robot.stop()
```

</details>

---

## The Complete Maze Explorer

Now let's put it all together into a loop:

1. **Scan** walls in current cell
2. **Record** walls and mark cell as visited
3. **Choose** an unvisited neighbor
4. **Move** there with `move_to_wall()`
5. **Repeat** until no unvisited neighbors

```python
import time
from evabot import Robot, MecanumDrive, RPLidarC1

robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1()
robot.start()

time.sleep(3)

# Direction helpers
DIR_DELTA = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}
OPPOSITE = {0: 180, 180: 0, 90: 270, 270: 90}
DIR_NAMES = {0: "Front", 90: "Right", 180: "Back", 270: "Left"}

# Map
visited = set()
walls = {}

def set_wall(x, y, direction, has_wall):
    walls[(x, y, direction)] = has_wall
    dx, dy = DIR_DELTA[direction]
    walls[(x + dx, y + dy, OPPOSITE[direction])] = has_wall

# Start at (0, 0)
x, y = 0, 0

for step in range(100):  # safety limit
    print(f"\n--- Cell ({x}, {y}) - Step {step + 1} ---")

    # 1. Scan walls
    visited.add((x, y))
    for angle in [0, 90, 180, 270]:
        dist, _, q = robot.lidar.check_wall(angle)
        has_wall = dist is not None and q is not None and q > 0.3 and dist < 0.25
        set_wall(x, y, angle, has_wall)
        status = f"{dist*100:.1f}cm WALL" if has_wall else "OPEN"
        print(f"  {DIR_NAMES[angle]:6s}: {status}")

    # 2. Find unvisited neighbor (priority: left, back, right, front)
    next_move = None
    for direction in [270, 180, 90, 0]:
        dx, dy = DIR_DELTA[direction]
        nx, ny = x + dx, y + dy
        if walls.get((x, y, direction)) is False and (nx, ny) not in visited:
            next_move = (direction, nx, ny)
            break

    if next_move is None:
        print("  No unvisited neighbors - done!")
        break

    direction, nx, ny = next_move
    print(f"  Moving {DIR_NAMES[direction]} -> ({nx}, {ny})")

    # 3. Move!
    robot.move_to_wall(direction, max_travel=0.30)
    x, y = nx, ny

print(f"\nExplored {len(visited)} cells!")
robot.drive.halt()
robot.stop()
```

**That's the whole maze explorer!** About 40 lines of actual logic.

---

### Exercise 6.3: Add Timing

Add timing to measure how long the exploration takes. Print total time and average time per cell.

<details>
<summary>Solution</summary>

```python
# Add at the start, before the loop:
t_start = time.time()

# Change the final print to:
t_total = time.time() - t_start
print(f"\nExplored {len(visited)} cells in {t_total:.1f}s")
print(f"Average: {t_total/len(visited):.1f}s per cell")
```

</details>

---

### Exercise 6.4: Faster Speed

Make the robot explore faster by passing a higher speed to `move_to_wall()`.

<details>
<summary>Solution</summary>

```python
# Change the move line to:
robot.move_to_wall(direction, speed=0.5)
```

The robot moves faster but still stops safely - `move_to_wall()` watches the walls at all times.

**Warning:** Very high speeds (>0.8) might be too fast for the lidar to react. Start with 0.3 and increase gradually.

</details>

---

## How move_to_wall() Works Inside

You've been using `move_to_wall()` as a black box. Here's what happens inside:

```python
# Simplified version of what move_to_wall does:
while True:
    # 1. Read the wall ahead
    distance, angle, quality = robot.lidar.check_wall(direction)

    # 2. Close enough? Stop!
    if distance <= stop_distance:
        robot.drive.halt()
        return

    # 3. Read ALL other walls
    for wall_dir in [0, 90, 180, 270]:
        d, a, q = robot.lidar.check_wall(wall_dir)

        # Too close to a side wall? Push away!
        if d < stop_distance:
            # Add sideways movement away from wall

        # Use wall angle for alignment
        # Average all wall angles for smooth rotation

    # 4. Set movement target
    robot.drive.set_target_position(dx, dy, dtheta)
```

**Key ideas:**
- Reads walls continuously (not just once)
- Pushes away from walls it's too close to
- Aligns to all visible walls at once
- Uses `set_target_position()` for smooth motor control

---

## What's Missing: Backtracking

Our explorer has one big limitation: when all neighbors are visited, it stops. In a larger maze, it might get stuck in a dead end with unvisited cells elsewhere.

```
+---+---+---+
|   |       |
+   +---+   +
| R |   |   |    R is stuck! All neighbors visited.
+   +   +   +    But top-right cell is still unvisited.
| . | . | . |
+---+---+---+
```

**The fix:** When stuck, backtrack along the path you came from until you find a cell with unvisited neighbors. This is called **Depth-First Search (DFS)**.

We'll add backtracking in a future chapter!

---

## Summary

You learned:

- Scan walls with `check_wall()` to detect walls vs openings
- Use `move_to_wall()` for safe cell-to-cell movement
- Track visited cells with a Python `set`
- Record walls from both sides with a `dict`
- Choose next cell using priority order (left-first exploration)
- Build a complete maze explorer in ~40 lines

**Key pattern for maze exploration:**
```python
while True:
    # Scan walls in current cell
    # Record walls in map
    # Find unvisited neighbor
    # Move there with robot.move_to_wall(direction, max_travel=0.30)
```

---

## What's Next?

In Chapter 7, you'll learn:
- **Backtracking** - Return to previous cells when stuck
- **Path planning** - Find the shortest path between cells
- **Larger mazes** - Navigate 5x5 and 10x10 mazes
