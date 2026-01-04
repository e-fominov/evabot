# Chapter 3: Multiple Motors

## What You'll Learn

Time to level up! You're going to control **4 motors at the same time** to make a real robot that can move around.

In this chapter you'll:
- Control 2 motors together
- Control all 4 motors for a wheeled robot
- Make cool movement patterns
- Understand how robots move

## How Robots Move

### One Motor vs Multiple Motors

**One motor:** Can only spin in place
- Good for: Fans, spinning things, one moving part

**Multiple motors:** Can make things move around!
- 2 motors: Can go forward/backward and turn (like a tank)
- 4 motors: Can move in ANY direction (forward, sideways, diagonal, spinning)

### Meet Your Robot's Motors

Your robot has 4 motors, one for each wheel:

```
      FRONT
   FL      FR
   (4)     (2)

   BL      BR
   (3)     (1)
      BACK
```

Each motor has a number:
- **FL (Front-Left)** = Motor 4
- **FR (Front-Right)** = Motor 2
- **BL (Back-Left)** = Motor 3
- **BR (Back-Right)** = Motor 1

**Remember:** These numbers stay the same for all our programs!

---

## Lesson 2.1: Two Motors Together

**Goal:** Make two motors spin at the same time!

### The Code

```python
from evabot import Motor
import time

# Create two motors
motor1 = Motor(1)  # Back-right wheel
motor2 = Motor(2)  # Front-right wheel

# Wake them both up
motor1.start()
motor2.start()

# Make them both go forward
motor1.run(30)
motor2.run(30)
time.sleep(3)

# Stop them both
motor1.stop()
motor2.stop()
```

**Try it:**
```bash
robot lesson 2.1
cd lesson2_1
robot run solution.py
```

Both motors should spin together!

### Making Them Do Different Things

**Same direction (robot goes straight):**
```python
motor1.run(30)   # Right side forward
motor2.run(30)   # Right side forward
# Robot moves forward!
```

**Opposite directions (robot turns):**
```python
motor1.run(30)    # One motor forward
motor2.run(-30)   # Other motor backward
# Robot spins in a circle!
```

**Different speeds (robot curves):**
```python
motor1.run(60)   # Right motor faster
motor2.run(20)   # Right motor slower
# Robot curves!
```

### Important: Send Commands Together!

**Good way (motors move together):**
```python
motor1.run(30)    # Tell motor 1 to go
motor2.run(30)    # Tell motor 2 to go
time.sleep(3)     # Now wait
```

**Bad way (motors don't move together):**
```python
motor1.run(30)
time.sleep(3)      # Motor 1 moves alone
motor2.run(30)     # Motor 2 hasn't started yet!
time.sleep(3)
```

Always tell ALL motors what to do, THEN wait!

### Using a List

Instead of writing `motor1`, `motor2` over and over, use a list:

```python
# Create motors in a list
motors = [Motor(1), Motor(2)]

# Start all motors
for motor in motors:
    motor.start()

# Run all motors
for motor in motors:
    motor.run(30)

time.sleep(3)

# Stop all motors
for motor in motors:
    motor.stop()
```

This is super helpful when you have many motors!

### Challenges

**1. Alternating Motors**
Make motor 1 spin, then motor 2 spin, then motor 1 again:

```python
motor1.start()
motor2.start()

motor1.run(30)
time.sleep(1)
motor1.hold()

motor2.run(30)
time.sleep(1)
motor2.hold()

motor1.run(30)
time.sleep(1)
motor1.hold()

motor1.stop()
motor2.stop()
```

**2. Speed Wave**
Make both motors gradually speed up together:

```python
motor1.start()
motor2.start()

for speed in range(10, 101, 10):
    motor1.run(speed)
    motor2.run(speed)
    time.sleep(1)

motor1.stop()
motor2.stop()
```

---

## Lesson 2.2: Four Motors (Your Robot!)

**Goal:** Control all 4 wheels to make your robot move!

### Creating All Four Motors

```python
from evabot import Motor

# Create all 4 motors
fl = Motor(4)  # Front-left
fr = Motor(2)  # Front-right
bl = Motor(3)  # Back-left
br = Motor(1)  # Back-right

# Wake them all up
fl.start()
fr.start()
bl.start()
br.start()

# Or use a loop!
motors = [fl, fr, bl, br]
for motor in motors:
    motor.start()
```

### Making Your Robot Move Forward

To go forward, ALL wheels spin the same direction:

```python
fl.run(40)
fr.run(40)
bl.run(40)
br.run(40)
time.sleep(3)  # Go forward for 3 seconds
```

Your robot should roll forward!

### Making Your Robot Spin

To spin in place, left wheels go one way, right wheels go the other way:

```python
# Left wheels forward, right wheels backward = Spin right
fl.run(40)
bl.run(40)
fr.run(-40)
br.run(-40)
time.sleep(2)  # Spin for 2 seconds
```

Your robot should spin in a circle!

### The Magic of Mecanum Wheels

Your robot has special wheels called "mecanum wheels." They can move sideways!

**Diagonal movement:**
```python
# Opposite corners same direction
fl.run(40)
br.run(40)
fr.run(-40)
bl.run(-40)
time.sleep(2)
```

Your robot moves diagonally! This is like magic - regular wheels can't do this!

### Complete Movement Example

```python
from evabot import Motor
import time

# Create all motors
fl, fr, bl, br = Motor(4), Motor(2), Motor(3), Motor(1)

# Start all
for m in [fl, fr, bl, br]:
    m.start()

print("Going forward...")
for m in [fl, fr, bl, br]:
    m.run(40)
time.sleep(2)
for m in [fl, fr, bl, br]:
    m.hold()

time.sleep(0.5)

print("Spinning right...")
fl.run(40)
bl.run(40)
fr.run(-40)
br.run(-40)
time.sleep(2)
for m in [fl, fr, bl, br]:
    m.hold()

time.sleep(0.5)

print("Going diagonal...")
fl.run(40)
br.run(40)
fr.run(-40)
bl.run(-40)
time.sleep(2)

# Stop everything
for m in [fl, fr, bl, br]:
    m.stop()

print("Done!")
```

**Try it:**
```bash
robot lesson 2.2
cd lesson2_2
robot run solution.py
```

### Checking Each Motor

Want to make sure all motors work? Test them one by one:

```python
motors = {
    'FL': Motor(4),
    'FR': Motor(2),
    'BL': Motor(3),
    'BR': Motor(1)
}

for motor in motors.values():
    motor.start()

# Test each motor
for name, motor in motors.items():
    print(f"\nTesting {name}...")
    motor.run(40)
    time.sleep(1)
    motor.hold()
    print(f"{name} position: {motor.get_position()}")
    time.sleep(0.5)

for motor in motors.values():
    motor.stop()
```

All motors should move! If one doesn't, check its connections.

---

## Lesson 2.3: Movement Patterns

**Goal:** Create cool patterns by combining motor movements!

### Pattern 1: Drive Forward

```python
def drive_forward(motors, speed, duration):
    """All motors same direction"""
    for motor in motors:
        motor.run(speed)
    time.sleep(duration)
    for motor in motors:
        motor.hold()

# Use it
motors = [Motor(i) for i in [1, 2, 3, 4]]
for m in motors:
    m.start()

drive_forward(motors, 40, 3)  # Forward for 3 seconds

for m in motors:
    m.stop()
```

### Pattern 2: Spin in Circle

```python
def spin_right(fl, fr, bl, br, speed, duration):
    """Spin clockwise"""
    # Left side forward
    fl.run(speed)
    bl.run(speed)
    # Right side backward
    fr.run(-speed)
    br.run(-speed)

    time.sleep(duration)

    # Stop all
    for m in [fl, fr, bl, br]:
        m.hold()

# Use it
fl, fr, bl, br = Motor(4), Motor(2), Motor(3), Motor(1)
for m in [fl, fr, bl, br]:
    m.start()

spin_right(fl, fr, bl, br, 40, 2)

for m in [fl, fr, bl, br]:
    m.stop()
```

### Pattern 3: Move Diagonal

```python
def move_diagonal(fl, fr, bl, br, speed, duration):
    """Diagonal movement (mecanum magic!)"""
    # Opposite corners together
    fl.run(speed)
    br.run(speed)
    fr.run(-speed)
    bl.run(-speed)

    time.sleep(duration)

    for m in [fl, fr, bl, br]:
        m.hold()
```

### Pattern 4: Dance Move!

Combine movements to make your robot dance:

```python
fl, fr, bl, br = Motor(4), Motor(2), Motor(3), Motor(1)
for m in [fl, fr, bl, br]:
    m.start()

print("Robot dance starting!")

# Forward
print("Step 1: Forward!")
for m in [fl, fr, bl, br]:
    m.run(40)
time.sleep(1)
for m in [fl, fr, bl, br]:
    m.hold()

# Spin left
print("Step 2: Spin left!")
fl.run(-40)
bl.run(-40)
fr.run(40)
br.run(40)
time.sleep(1)
for m in [fl, fr, bl, br]:
    m.hold()

# Diagonal right
print("Step 3: Diagonal!")
fl.run(40)
br.run(40)
fr.run(-40)
bl.run(-40)
time.sleep(1)
for m in [fl, fr, bl, br]:
    m.hold()

# Spin right
print("Step 4: Spin right!")
fl.run(40)
bl.run(40)
fr.run(-40)
br.run(-40)
time.sleep(1)

print("Dance complete!")
for m in [fl, fr, bl, br]:
    m.stop()
```

**Try it:**
```bash
robot lesson 2.3
cd lesson2_3
robot run solution.py
```

### Your Turn: Create Your Own Patterns!

**Challenge 1: Figure-8**
Can you make your robot move in a figure-8 shape?
- Hint: Combine forward movement with spinning

**Challenge 2: Square**
Make your robot drive in a square:
- Forward
- Turn right 90 degrees
- Forward
- Turn right 90 degrees
- (repeat 2 more times)

**Challenge 3: Speed Wave**
Make all motors gradually speed up and slow down together:

```python
# Speed up
for speed in range(10, 101, 10):
    for m in motors:
        m.run(speed)
    time.sleep(0.5)

# Slow down
for speed in range(100, 9, -10):
    for m in motors:
        m.run(speed)
    time.sleep(0.5)
```

---

## Understanding Robot Movement

### How Do 4 Wheels Make Different Movements?

**All same direction = Forward/Backward**
```
FL → → FR
BL → → BR
Result: Robot goes forward →
```

**Left forward, Right backward = Spin Right**
```
FL → → FR
       ← ←
BL → → BR
       ← ←
Result: Robot spins ↻
```

**Diagonal (Mecanum Magic!)**
```
FL → →  ← ← FR
       ↘
BL ← ←  → → BR
Result: Robot moves diagonally ↘
```

The special mecanum wheels let you move sideways - regular wheels can't do this!

### Why Do Motors Need Different Speeds Sometimes?

Motors aren't perfect - they might spin at slightly different speeds even when you tell them the same number. This is normal!

You can check by reading their positions:

```python
fl.run(40)
fr.run(40)
bl.run(40)
br.run(40)
time.sleep(2)

print(f"FL moved: {fl.get_position()} pulses")
print(f"FR moved: {fr.get_position()} pulses")
print(f"BL moved: {bl.get_position()} pulses")
print(f"BR moved: {br.get_position()} pulses")
```

The numbers should be close (within 100-200 pulses). Later you'll learn how to make them even more precise!

---

## Important Tips for Multiple Motors

### Tip 1: Always Start All Motors First

```python
# Good!
motors = [Motor(1), Motor(2), Motor(3), Motor(4)]
for m in motors:
    m.start()  # Start all first

# Now use them
for m in motors:
    m.run(40)
```

### Tip 2: Send Commands to All Motors, Then Wait

```python
# Good! (motors move together)
motor1.run(40)
motor2.run(40)
motor3.run(40)
motor4.run(40)
time.sleep(3)  # Wait after commanding all

# Bad! (motors move one at a time)
motor1.run(40)
time.sleep(3)  # Motor 1 moves alone
motor2.run(40)
time.sleep(3)  # Motor 2 hasn't started yet
```

### Tip 3: Always Stop All Motors at the End

```python
# Use a loop to stop all motors
for motor in motors:
    motor.stop()
```

Or even better, use `try/finally` to make sure motors ALWAYS stop:

```python
motors = [Motor(i) for i in [1, 2, 3, 4]]
try:
    # Start motors
    for m in motors:
        m.start()

    # Your robot code here
    for m in motors:
        m.run(40)
    time.sleep(3)

finally:
    # This ALWAYS runs, even if there's an error
    for m in motors:
        m.stop()
```

---

## What You've Learned

Awesome work! You can now:

✅ Control 2 motors together
✅ Control all 4 motors for a robot
✅ Make robots go forward, backward, spin, and diagonal
✅ Create movement patterns
✅ Check if all motors are working

## Next: Better Robot Control!

You've learned the basics of controlling motors. Next, you'll learn to make robots that can:
- Move in meters per second (not just RPM)
- Know exactly where they are
- Drive in straight lines automatically
- Follow paths

Ready? → [Chapter 4: Drive Systems](chapter4_drive_systems.md)
