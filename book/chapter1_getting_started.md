# Chapter 1: Getting Started

## Welcome to Robotics!

You're about to learn how to control real robots! By the end of this chapter, you'll make a motor spin, stop, and follow your commands.

## What You'll Need

- A computer (where you write code)
- A robot with motors (Raspberry Pi with motors attached)
- The `robot` command installed
- Your brain and curiosity!

## Installing EvaBot

### Step 1: Get the Code

Open your terminal and type:

```bash
git clone https://github.com/e-fominov/evabot.git
cd evabot
pip install -e .
```

This downloads the robot code and installs it on your computer.

### Step 2: Tell Your Computer About Your Robot

```bash
robot setup
```

You'll see questions like:
- **Robot hostname**: Where is your robot? (like `192.168.1.100` or `rpi`)
- **Username**: Usually `pi`
- **Directory**: Where code goes on the robot (usually `/home/pi/evabot`)

Just answer the questions and you're done! This saves the settings so you don't have to type them again.

### Step 3: Put EvaBot on Your Robot

```bash
robot install
```

This copies all the robot code to your robot and sets everything up. It takes a couple minutes - perfect time for a snack!

## How Does This Work?

Think of it like this:
1. **Your computer** is like your brain - where you write the plan
2. **The robot** is like your hands - where the action happens
3. **The `robot` command** is like a messenger - it takes your plan to your hands

When you run:
```bash
robot run my_program.py
```

Here's what happens:
1. Your program copies to the robot
2. The robot runs your program
3. You see what's happening in real-time on your screen!

It's like remote control, but with code instead of a joystick.

## Your First Robot Program

Let's make a motor spin!

### Create Your Workspace

```bash
cd ~
robot lesson 1.1 --solution
cd lesson1_1
```

This creates a folder called `lesson1_1` with everything you need:
- `README.md` - Instructions for this lesson
- `template.py` - Where you write code
- `solution.py` - Working example (we used `--solution` to get this)

### Look at the Code

```bash
cat solution.py
```

You'll see:

```python
from evabot import Motor
import time

# Create a motor (motor number 1)
motor = Motor(1)

# Wake up the motor
motor.start()

# Spin at 30 RPM (rotations per minute)
motor.run(30)

# Let it spin for 3 seconds
time.sleep(3)

# Stop the motor
motor.stop()
```

### Run It!

```bash
robot run solution.py
```

**Watch your robot!** The motor should spin for 3 seconds then stop.

On your screen you'll see:
```
CanBus: Opened can0 @ 500000bps
Servo42D_1: Ready on CAN ID 1
Servo42D_1: Stopped
```

This tells you:
- The robot's messaging system started
- Motor #1 is ready
- Motor stopped (at the end)

## Understanding the Code

Let's break down what each line does:

### 1. Import Motor

```python
from evabot import Motor
```

This is like getting a tool from a toolbox. We're getting the `Motor` tool.

### 2. Create Motor

```python
motor = Motor(1)
```

This creates a connection to motor number 1. Think of it like labeling which motor you want to control.

Motors are numbered 1, 2, 3, 4. For a robot with 4 wheels, each wheel has its own number.

### 3. Start Motor

```python
motor.start()
```

This wakes up the motor and gets it ready. The motor shaft locks (you can't turn it by hand anymore).

### 4. Make It Spin

```python
motor.run(30)
```

This tells the motor: "Spin at 30 RPM!"

**What's RPM?** Rotations Per Minute = how many full spins in 1 minute
- 30 RPM = Pretty slow (half a spin per second)
- 60 RPM = Medium speed (1 spin per second)
- 120 RPM = Fast! (2 spins per second)

### 5. Wait

```python
time.sleep(3)
```

Your code pauses for 3 seconds while the motor spins. Without this, your code would immediately jump to the next line and stop the motor!

### 6. Stop Motor

```python
motor.stop()
```

The motor stops spinning and the shaft unlocks (you can turn it by hand again).

## Experiments to Try

### Experiment 1: Change the Speed

Try different speeds in `motor.run()`:

```python
motor.run(10)   # Super slow
motor.run(60)   # Medium
motor.run(120)  # Fast!
```

What's the fastest your motor can go without making weird sounds?

### Experiment 2: Spin Longer

Change the sleep time:

```python
time.sleep(10)  # Spin for 10 seconds instead!
```

### Experiment 3: Multiple Spins

Try this pattern:

```python
motor.start()

motor.run(30)
time.sleep(2)

motor.run(60)   # Speed up!
time.sleep(2)

motor.run(30)   # Slow down
time.sleep(2)

motor.stop()
```

The motor should speed up in the middle!

## Important Motor Rules

### Rule 1: Always Call `start()` First

```python
motor = Motor(1)
motor.start()      # Wake up the motor first!
motor.run(30)      # Now you can spin it
```

Without `start()`, the motor won't do anything.

### Rule 2: Always Call `stop()` at the End

```python
motor.run(30)
time.sleep(3)
motor.stop()       # Put the motor to sleep
```

This unlocks the motor shaft so you can move it by hand.

### Rule 3: Safety First!

The robot has a safety feature: if your code crashes or you press Ctrl+C, all motors automatically stop. This prevents accidents!

## Troubleshooting

### "My motor doesn't spin!"

**Check:**
1. Is the motor plugged in to power? (needs 24V power supply)
2. Is the robot turned on?
3. Can you ping the robot? Try `ping rpi` in terminal
4. Is it motor number 1? (check the motor's ID number)

### "I get 'Robot configuration not found'"

Run this first:
```bash
robot setup
```

### "The motor spins then stops right away"

That's okay! Maybe your `time.sleep()` is very short. Try `time.sleep(5)` for 5 seconds of spinning.

## What You Learned

Awesome! You can now:
- ✅ Install robot code
- ✅ Connect to your robot
- ✅ Make a motor spin
- ✅ Control how fast it spins
- ✅ Stop the motor

## Next Challenge

Ready to do more? → [Chapter 2: Motor Control](chapter2_motor_basics.md)

You'll learn to:
- Change speed while the motor is running
- Make it spin backward
- Read how far the motor has turned
- Move exact distances
