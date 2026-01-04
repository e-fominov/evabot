# EvaBot Programming Reference

Quick reference for all EvaBot commands and functions. Perfect for looking up how to do something!

## Table of Contents

- [Motor Class](#motor-class)
- [Constants](#constants)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Motor Class

### Creating a Motor

```python
from evabot import Motor

motor = Motor(can_id)
```

**Parameters:**
- `can_id`: Motor number (1, 2, 3, or 4)
  - Motor 1 = Back-Right wheel
  - Motor 2 = Front-Right wheel
  - Motor 3 = Back-Left wheel
  - Motor 4 = Front-Left wheel

**Example:**
```python
motor1 = Motor(1)      # Back-right motor
motor_fl = Motor(4)    # Front-left motor
```

---

### Starting and Stopping

#### `start()`
Wake up the motor and get it ready.

```python
motor.start()
```

**What it does:**
- Connects to the robot
- Locks the motor shaft (can't turn by hand)
- Gets motor ready to receive commands

**When to use:** At the beginning of your program, after creating the motor.

**Example:**
```python
motor = Motor(1)
motor.start()    # Motor is now ready!
```

---

#### `stop()`
Stop the motor and clean up.

```python
motor.stop()
```

**What it does:**
- Stops the motor from moving
- Unlocks the shaft (can turn by hand again)
- Cleans up and releases resources

**When to use:** At the end of your program.

**Example:**
```python
motor.run(30)
time.sleep(3)
motor.stop()     # All done, clean up
```

---

### Speed Control

#### `run(speed_rpm)`
Make the motor spin at a specific speed.

```python
motor.run(speed_rpm)
```

**Parameters:**
- `speed_rpm`: How fast to spin
  - Positive number = Forward (clockwise)
  - Negative number = Backward (counter-clockwise)
  - Zero = Stop moving
  - Range: -300 to +300 RPM (depends on your motor)

**What it does:**
- Motor spins continuously at the given speed
- Keeps spinning until you tell it a different speed
- Background system keeps sending the command (so motor doesn't time out)

**Examples:**
```python
motor.run(30)     # Spin forward at 30 RPM
motor.run(-40)    # Spin backward at 40 RPM
motor.run(0)      # Stop (same as hold())
motor.run(120)    # Fast! (2 rotations per second)
```

**Speed Reference:**
```
30 RPM = Half a spin per second (slow)
60 RPM = 1 spin per second (medium)
120 RPM = 2 spins per second (fast)
```

---

#### `hold()`
Stop moving but keep shaft locked.

```python
motor.hold()
```

**What it does:**
- Motor stops spinning
- Shaft stays locked (can't turn it by hand)
- Motor still has power and is ready to move again

**When to use:** When you want to pause but keep the motor ready.

**Example:**
```python
motor.run(30)
time.sleep(2)
motor.hold()       # Stop but stay ready
time.sleep(1)
motor.run(40)      # Start again quickly
```

**Note:** `motor.hold()` is the same as `motor.run(0)`

---

#### `disable()`
Stop and unlock the motor shaft.

```python
motor.disable()
```

**What it does:**
- Motor stops spinning
- Shaft unlocks (you can turn it by hand)
- Motor saves power

**When to use:** When you're done and want to save power or move the motor by hand.

**Example:**
```python
motor.run(30)
time.sleep(2)
motor.disable()    # Stop and unlock
# Now you can turn the motor shaft by hand!
```

---

### Position Reading

#### `get_position()`
Find out how far the motor has turned.

```python
position = motor.get_position()
```

**Returns:** Number of pulses (steps) the motor has moved
- 3200 pulses = 1 full rotation
- 1600 pulses = half rotation
- 800 pulses = quarter rotation

**Example:**
```python
start = motor.get_position()
motor.run(60)
time.sleep(1)
end = motor.get_position()

distance = end - start
print(f"Motor moved {distance} pulses")
print(f"That's {distance / 3200} rotations")
```

**Converting pulses:**
```python
# Pulses to rotations
rotations = pulses / 3200

# Pulses to degrees
degrees = pulses / 8.889    # Because 3200 ÷ 360 = 8.889
```

---

#### `get_speed()`
Get the current commanded speed.

```python
speed = motor.get_speed()
```

**Returns:** The speed you last told the motor (in RPM)

**Example:**
```python
motor.run(30)
print(motor.get_speed())  # Prints: 30.0

motor.run(-40)
print(motor.get_speed())  # Prints: -40.0
```

---

### Position Control

#### `zero_position()`
Set the current position as zero.

```python
motor.zero_position()
```

**What it does:**
- Marks current position as the zero reference point
- All future `move_to()` commands are measured from here

**Returns:** `True` if successful, `False` if failed

**When to use:** Before using `move_to()` for the first time.

**Example:**
```python
motor.start()
motor.zero_position()           # This is zero now

motor.move_to(90, 40, 'degrees')  # Move to 90° from zero
motor.move_to(0, 30, 'degrees')   # Return to zero
```

---

#### `move_by(distance, speed, unit)`
Move by a specific amount from current position.

```python
motor.move_by(distance, speed, unit='degrees')
```

**Parameters:**
- `distance`: How far to move
  - Positive = Forward
  - Negative = Backward
- `speed`: How fast to move (RPM, 0-300)
- `unit`: Either `'degrees'` or `'rotations'` (default: `'degrees'`)

**What it does:**
- Moves the specified distance
- Stops automatically when done
- **Your code waits** until movement completes

**Returns:** `True` if successful, `False` if failed

**Examples:**
```python
# Move 90 degrees forward
motor.move_by(90, 40, 'degrees')

# Move 180 degrees backward
motor.move_by(-180, 30, 'degrees')

# Move 2 full rotations
motor.move_by(2, 50, 'rotations')

# Move half a rotation
motor.move_by(0.5, 40, 'rotations')
```

**Important:** This blocks - your code waits until the motor reaches its target!

```python
print("Starting...")
motor.move_by(180, 40, 'degrees')  # Code waits here
print("Finished!")  # Only prints after motor stops
```

---

#### `move_to(position, speed, unit)`
Move to a specific position (from zero).

```python
motor.move_to(position, speed, unit='degrees')
```

**Parameters:**
- `position`: Where to go (measured from zero point)
- `speed`: How fast to move (RPM, 0-300)
- `unit`: Either `'degrees'` or `'rotations'` (default: `'degrees'`)

**What it does:**
- Moves to the absolute position
- Stops automatically when done
- **Your code waits** until movement completes

**Returns:** `True` if successful, `False` if failed

**Examples:**
```python
motor.zero_position()              # Set zero first!

motor.move_to(90, 40, 'degrees')   # Go to 90°
motor.move_to(180, 50, 'degrees')  # Go to 180°
motor.move_to(-90, 30, 'degrees')  # Go to -90°
motor.move_to(0, 40, 'degrees')    # Return to zero

# Using rotations
motor.move_to(2, 50, 'rotations')  # Go to 2 full rotations
motor.move_to(0, 30, 'rotations')  # Back to zero
```

**Important:** Call `zero_position()` first, or the motor won't know where zero is!

---

### Emergency Functions

#### `emergency_stop()`
Stop everything immediately!

```python
motor.emergency_stop()
```

**What it does:**
- Stops motor immediately
- Disables motor (releases shaft)
- Clears all pending commands

**When to use:** In emergencies or error conditions.

**Example:**
```python
try:
    motor.run(100)
    time.sleep(10)
except KeyboardInterrupt:
    motor.emergency_stop()  # User pressed Ctrl+C
    print("Emergency stop!")
```

**Note:** Motors automatically emergency stop when your program crashes or exits!

---

## Constants

Useful numbers for calculations:

```python
Motor.PULSES_PER_ROTATION = 3200    # 3200 pulses = 1 full rotation
Motor.PULSES_PER_DEGREE = 8.889     # ~8.889 pulses = 1 degree
```

**Using constants:**
```python
# Convert position to rotations
rotations = motor.get_position() / Motor.PULSES_PER_ROTATION

# Convert position to degrees
degrees = motor.get_position() / Motor.PULSES_PER_DEGREE
```

---

## Common Patterns

### Basic Motor Pattern

```python
from evabot import Motor
import time

motor = Motor(1)
motor.start()

# Your code here
motor.run(30)
time.sleep(3)

motor.stop()
```

### Multiple Motors Pattern

```python
from evabot import Motor
import time

# Create all motors
motors = [Motor(i) for i in [1, 2, 3, 4]]

# Start all
for m in motors:
    m.start()

# Use all (tell all motors what to do first!)
for m in motors:
    m.run(40)
time.sleep(3)

# Stop all
for m in motors:
    m.stop()
```

### Safe Pattern (Always Stops)

```python
from evabot import Motor
import time

motor = Motor(1)
try:
    motor.start()

    # Your code here
    motor.run(30)
    time.sleep(3)

finally:
    motor.stop()  # ALWAYS runs, even if there's an error!
```

### Position Control Pattern

```python
from evabot import Motor

motor = Motor(1)
motor.start()

# Set zero point
motor.zero_position()

# Move to exact positions
motor.move_by(90, 40, 'degrees')
motor.move_by(90, 40, 'degrees')
motor.move_to(0, 30, 'degrees')  # Back to zero

motor.stop()
```

### Four-Wheel Robot Pattern

```python
from evabot import Motor
import time

# Create motors for mecanum robot
fl = Motor(4)  # Front-left
fr = Motor(2)  # Front-right
bl = Motor(3)  # Back-left
br = Motor(1)  # Back-right

# Start all
for m in [fl, fr, bl, br]:
    m.start()

# Forward
for m in [fl, fr, bl, br]:
    m.run(40)
time.sleep(2)

# Spin right
fl.run(40)
bl.run(40)
fr.run(-40)
br.run(-40)
time.sleep(2)

# Stop all
for m in [fl, fr, bl, br]:
    m.stop()
```

---

## Troubleshooting

### Motor doesn't move

**Possible causes:**
1. Did you call `motor.start()`?
2. Is the motor powered? (24V power supply connected?)
3. Is it the right motor number? (1, 2, 3, or 4)
4. Is `time.sleep()` long enough to see movement?

**Solution:**
```python
motor = Motor(1)
motor.start()        # Don't forget this!
motor.run(30)
time.sleep(3)        # Make sure this is long enough
motor.stop()
```

### "Robot configuration not found"

**Cause:** Haven't run `robot setup` yet.

**Solution:**
```bash
robot setup
```

### Position control doesn't work

**Cause:** Forgot to call `zero_position()` first.

**Solution:**
```python
motor.start()
motor.zero_position()  # Set zero BEFORE using move_to()
motor.move_to(90, 40, 'degrees')
```

### Motors spin at different speeds

**Cause:** Normal! Motors aren't perfect.

**Check:** Read positions to see actual difference:
```python
print(f"Motor 1: {motor1.get_position()} pulses")
print(f"Motor 2: {motor2.get_position()} pulses")
```

Differences of 100-200 pulses are normal.

### Motor keeps spinning after program ends

**Cause:** This should NEVER happen! It's a bug.

**Emergency fix:**
```bash
robot shell
# On robot, run:
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000
```

**Report it:** This is a safety bug - please report it!

### Code waits forever at `move_by()` or `move_to()`

**Possible causes:**
1. Motor can't reach target (blocked by something)
2. Target distance too large
3. Motor not enabled

**Solution:** Use shorter distances and make sure motor can move freely.

---

## Quick Reference Card

```
STARTING & STOPPING
motor = Motor(1)    Create motor
motor.start()       Wake up motor
motor.stop()        Stop and cleanup

SPEED CONTROL
motor.run(30)       Spin at 30 RPM forward
motor.run(-30)      Spin at 30 RPM backward
motor.run(0)        Stop moving (same as hold)
motor.hold()        Stop but keep locked
motor.disable()     Stop and unlock

POSITION READING
pos = motor.get_position()   Get position in pulses
speed = motor.get_speed()    Get current speed

POSITION CONTROL
motor.zero_position()                   Set current as zero
motor.move_by(90, 40, 'degrees')       Move 90° from here
motor.move_to(90, 40, 'degrees')       Go to 90° from zero
motor.move_by(2, 50, 'rotations')      Move 2 rotations
motor.move_to(0, 30, 'degrees')        Return to zero

EMERGENCY
motor.emergency_stop()       Stop immediately!

CONVERSIONS
3200 pulses = 1 rotation = 360 degrees
1600 pulses = 0.5 rotation = 180 degrees
800 pulses = 0.25 rotation = 90 degrees

60 RPM = 1 rotation per second
120 RPM = 2 rotations per second

rotations = pulses / 3200
degrees = pulses / 8.889
```

---

## Need More Help?

- **Book chapters**: Detailed explanations with examples
  - [Chapter 1: Getting Started](chapter1_getting_started.md)
  - [Chapter 2: Motor Basics](chapter2_motor_basics.md)
  - [Chapter 3: Multiple Motors](chapter3_multi_motor.md)

- **Lesson code**: See working examples in `lessons/` directory

- **Issues**: Report bugs at https://github.com/e-fominov/evabot/issues
