# Chapter 2: Motor Control

## What You'll Learn

In this chapter, you'll become a motor expert! You'll learn how to:
- Change motor speed while it's running
- Make motors spin backward
- See how far a motor has turned
- Make motors move exact distances (like "turn exactly 90 degrees")

## Lesson 1.1: Make It Spin

**Goal:** Get your first motor spinning!

### The Code

```bash
robot lesson 1.1
cd lesson1_1
robot run solution.py
```

Watch the motor! It should spin for 3 seconds then stop.

### What's Happening?

```python
from evabot import Motor
import time

motor = Motor(1)     # Connect to motor #1
motor.start()        # Wake it up
motor.run(30)        # Spin at 30 RPM
time.sleep(3)        # Wait 3 seconds
motor.stop()         # Stop and unlock
```

Think of the motor like a toy with an on/off switch:
- `motor.start()` = Turn it on
- `motor.run(30)` = Make it go at speed 30
- `motor.stop()` = Turn it off

### Try This!

**Make it spin faster:**
```python
motor.run(60)   # Twice as fast!
```

**Make it spin longer:**
```python
time.sleep(10)  # Spin for 10 seconds
```

---

## Lesson 1.2: Control Speed

**Goal:** Change the motor's speed while it's running!

### Speed Changes in Action

```python
motor.start()

print("Starting slow...")
motor.run(20)      # Slow
time.sleep(2)

print("Speeding up!")
motor.run(60)      # Faster
time.sleep(2)

print("Slowing down...")
motor.run(30)      # Medium
time.sleep(2)

print("Going backward!")
motor.run(-40)     # Reverse!
time.sleep(2)

motor.stop()
```

**Run it:**
```bash
robot lesson 1.2
cd lesson1_2
robot run solution.py
```

You should hear the motor speed up and slow down!

### Understanding Speed

**RPM means "Rotations Per Minute":**
- `motor.run(30)` = 30 spins in one minute (half a spin per second)
- `motor.run(60)` = 60 spins in one minute (1 spin per second)
- `motor.run(120)` = 120 spins in one minute (2 spins per second)

**Direction:**
- Positive number = Forward (clockwise)
- Negative number = Backward (counter-clockwise)
- Zero = Stop

```python
motor.run(50)    # Forward at 50 RPM
motor.run(-50)   # Backward at 50 RPM
motor.run(0)     # Stop
```

### Speed Ramp Challenge

Make the motor gradually speed up from 10 to 100 RPM:

```python
motor.start()

for speed in range(10, 101, 10):  # 10, 20, 30, ... 100
    print(f"Speed: {speed} RPM")
    motor.run(speed)
    time.sleep(1)

motor.stop()
```

---

## Lesson 1.3: Start and Stop

**Goal:** Learn different ways to stop a motor.

### Three Ways to Stop

**1. `hold()` - Stop but Stay Locked**

```python
motor.run(30)
time.sleep(2)
motor.hold()      # Stop moving, but shaft stays locked
```

The motor stops spinning but you still can't turn it by hand. It's like pressing "pause" on a video.

**When to use:** When you want to stop temporarily but keep the motor ready.

**2. `disable()` - Unlock the Shaft**

```python
motor.run(30)
time.sleep(2)
motor.disable()   # Stop and unlock shaft
```

The motor stops AND you can now turn it by hand. It's like putting the motor to sleep.

**When to use:** When you're done and want to save power or adjust the motor position by hand.

**3. `stop()` - Complete Stop**

```python
motor.run(30)
time.sleep(2)
motor.stop()      # Stop, unlock, and cleanup
```

This does everything: stops the motor, unlocks it, and cleans up. Use this at the end of your program.

### Try It Yourself

```bash
robot lesson 1.3
cd lesson1_3
robot run solution.py
```

The program will demonstrate all three ways to stop!

### When to Use Which?

Think of it like this:

```
hold() = Pause button
├─ Motor stops moving
├─ Shaft stays locked
└─ Ready to move again quickly

disable() = Sleep mode
├─ Motor stops moving
├─ Shaft unlocks (you can turn it)
└─ Saves power

stop() = Turn off
├─ Motor stops moving
├─ Shaft unlocks
└─ Complete cleanup (use at program end)
```

---

## Lesson 1.4: Read Position

**Goal:** Learn to see how far your motor has turned!

### The Motor's Built-in Counter

Every motor has a built-in counter (called an encoder) that counts how many times it spins. It's super precise - it can count **3200 steps per rotation**!

### Reading the Position

```python
motor.start()

# See where we started
start_position = motor.get_position()
print(f"Starting at: {start_position}")

# Spin for 2 seconds
motor.run(60)  # 60 RPM = 1 rotation per second
time.sleep(2)

# See where we ended
end_position = motor.get_position()
print(f"Ending at: {end_position}")

# Calculate how far we moved
distance = end_position - start_position
print(f"Moved {distance} steps")
print(f"That's about {distance / 3200} rotations")

motor.stop()
```

### Understanding the Numbers

The position is measured in "pulses" (also called steps):
- **3200 pulses** = 1 full rotation (360 degrees)
- **1600 pulses** = half a rotation (180 degrees)
- **800 pulses** = quarter rotation (90 degrees)

**To convert pulses to rotations:**
```python
rotations = pulses / 3200
```

**To convert pulses to degrees:**
```python
degrees = pulses / 8.889  # Because 3200 ÷ 360 = 8.889
```

### Watch It Count!

This program shows the position while the motor is running:

```python
motor.start()
motor.run(60)  # 1 rotation per second

# Show position 10 times
for i in range(10):
    pos = motor.get_position()
    rotations = pos / 3200
    print(f"Position: {pos:6d} pulses = {rotations:.2f} rotations")
    time.sleep(0.5)

motor.stop()
```

**Try it:**
```bash
robot lesson 1.4
cd lesson1_4
robot run solution.py
```

You'll see the number going up as the motor spins!

### Test Your Motor's Speed

Does your motor really spin at the speed you tell it?

```python
motor.start()

# Tell motor to do 60 RPM (1 rotation per second)
motor.run(60)

# Measure for exactly 1 second
start = motor.get_position()
time.sleep(1)
end = motor.get_position()

# How far did it go?
moved = end - start
print(f"Motor moved {moved} pulses")
print(f"Expected: 3200 pulses (1 rotation)")
print(f"Difference: {moved - 3200} pulses")

motor.stop()
```

Is it close to 3200? Perfect! Small differences (±100) are normal.

---

## Lesson 1.5: Move Exact Distance

**Goal:** Make the motor move exactly 90 degrees, or exactly 2 rotations, or any precise amount!

### The Magic of Position Control

Instead of saying "spin at 30 RPM," you can say "move exactly 90 degrees then stop."

This is super useful for:
- Robot arms (move joint exactly 45 degrees)
- Grippers (open exactly 30 degrees)
- Wheels (turn exactly 2 rotations)

### Setting Your Starting Point

First, tell the motor where "zero" is:

```python
motor.start()
motor.zero_position()  # This is zero now!
```

This marks the current position as your reference point. All movements will be measured from here.

### Moving by Exact Amounts

**Move 90 degrees forward:**
```python
motor.move_by(90, 40, 'degrees')
```

This means: "Move 90 degrees at speed 40 RPM, then stop automatically."

**Your code waits** until the movement finishes! It's like `time.sleep()` but it knows when the motor actually reaches its target.

### Complete Example

```python
motor.start()

# Set starting position as zero
motor.zero_position()
print("Position is now zero!")

# Move 90 degrees (quarter turn)
print("Moving 90 degrees...")
motor.move_by(90, 40, 'degrees')
print(f"Position now: {motor.get_position()} pulses")

# Move back to zero
print("Going back to zero...")
motor.move_to(0, 30, 'degrees')
print(f"Position now: {motor.get_position()} pulses")

# Full rotation
print("Doing a full rotation...")
motor.move_by(360, 50, 'degrees')
print(f"Position now: {motor.get_position()} pulses")

# Back to zero
motor.move_to(0, 40, 'degrees')

motor.stop()
```

**Try it:**
```bash
robot lesson 1.5
cd lesson1_5
robot run solution.py
```

### Two Ways to Move Exactly

**1. `move_by()` - Move FROM where you are**

```python
# Start at position 0
motor.zero_position()

# Move 90 degrees forward → now at 90
motor.move_by(90, 40, 'degrees')

# Move 90 more degrees forward → now at 180
motor.move_by(90, 40, 'degrees')

# Move 90 degrees backward → now at 90
motor.move_by(-90, 40, 'degrees')
```

Think of `move_by()` like taking steps: "take 5 steps forward" moves you relative to where you are now.

**2. `move_to()` - Go TO a specific position**

```python
# Start at position 0
motor.zero_position()

# Go to 90 degrees → moves to 90
motor.move_to(90, 40, 'degrees')

# Go to 180 degrees → moves to 180
motor.move_to(180, 40, 'degrees')

# Go to 0 degrees → moves back to 0
motor.move_to(0, 40, 'degrees')
```

Think of `move_to()` like going to a room number: "go to room 5" takes you there no matter where you started.

### Degrees vs Rotations

You can use either degrees or rotations:

**Degrees (for angles):**
```python
motor.move_by(90, 40, 'degrees')    # Quarter turn
motor.move_by(180, 40, 'degrees')   # Half turn
motor.move_by(360, 40, 'degrees')   # Full turn
```

**Rotations (for multiple spins):**
```python
motor.move_by(0.5, 40, 'rotations')  # Half turn
motor.move_by(1, 40, 'rotations')    # One full turn
motor.move_by(2.5, 40, 'rotations')  # Two and a half turns
```

Use degrees for small movements, rotations for big ones!

### Square Wave Challenge

Can you make the motor go back and forth like a square wave?

```python
motor.start()
motor.zero_position()

# Go back and forth 5 times
for i in range(5):
    motor.move_by(90, 40, 'degrees')   # Forward
    motor.move_by(-90, 40, 'degrees')  # Back

motor.stop()
```

### Clock Challenge

Make the motor act like a clock's minute hand:

```python
motor.start()
motor.zero_position()

# Start at 12 o'clock (0 degrees)
# Move to 3 o'clock (90 degrees)
# Then 6 o'clock (180 degrees)
# Then 9 o'clock (270 degrees)
# Back to 12 o'clock (0 degrees)

motor.move_to(90, 40, 'degrees')   # 3 o'clock
time.sleep(1)

motor.move_to(180, 40, 'degrees')  # 6 o'clock
time.sleep(1)

motor.move_to(270, 40, 'degrees')  # 9 o'clock
time.sleep(1)

motor.move_to(0, 40, 'degrees')    # 12 o'clock

motor.stop()
```

---

## Motor Command Cheat Sheet

Here's everything you can tell a motor to do:

### Starting and Stopping

```python
motor = Motor(1)      # Connect to motor #1
motor.start()         # Wake up the motor
motor.stop()          # Stop and cleanup (use at end)
```

### Speed Control (Continuous Spinning)

```python
motor.run(30)         # Spin forward at 30 RPM
motor.run(-30)        # Spin backward at 30 RPM
motor.run(0)          # Stop (but stay locked)
motor.hold()          # Same as run(0) - stop but stay locked
motor.disable()       # Stop and unlock shaft
```

### Position Reading

```python
pos = motor.get_position()     # Get current position in pulses
rotations = pos / 3200         # Convert to rotations
degrees = pos / 8.889          # Convert to degrees
```

### Position Control (Exact Movements)

```python
motor.zero_position()                    # Set current position as zero

motor.move_by(90, 40, 'degrees')         # Move 90 degrees from here
motor.move_by(-180, 30, 'degrees')       # Move 180 degrees backward
motor.move_by(2, 50, 'rotations')        # Move 2 full rotations

motor.move_to(90, 40, 'degrees')         # Go to 90 degrees (from zero)
motor.move_to(0, 30, 'degrees')          # Return to zero
motor.move_to(1.5, 50, 'rotations')      # Go to 1.5 rotations
```

### Understanding Numbers

```
3200 pulses = 1 full rotation = 360 degrees
1600 pulses = half rotation = 180 degrees
800 pulses = quarter rotation = 90 degrees

60 RPM = 1 rotation per second
120 RPM = 2 rotations per second
```

---

## What You've Learned

Amazing progress! You now know:

✅ Make motors spin at any speed
✅ Change speed while running
✅ Spin forward and backward
✅ Stop motors in different ways
✅ Read how far a motor has turned
✅ Move motors exact distances

## Next: Multiple Motors!

Ready for the next challenge? → [Chapter 3: Multiple Motors](chapter3_multi_motor.md)

You'll learn to:
- Control 4 motors at once
- Make them work together
- Create movement patterns
- Build a real drive system!
