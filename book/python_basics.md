# Python Basics for Robotics

## Introduction

Before you start programming robots, you need to know some Python basics. Don't worry - you only need to learn a few simple things to get started!

This chapter teaches you exactly what you need to control robots. Nothing more, nothing less.

**What you'll learn:**
- Writing and running Python programs
- Variables (storing information)
- Printing (showing messages)
- Math (doing calculations)
- If statements (making decisions)
- Loops (repeating things)
- Functions (reusing code)
- Importing (using tools)

**Time:** 1-2 hours

---

## Your First Python Program

### Creating a Python File

Python programs are text files that end with `.py`. Let's create one:

```bash
cd ~
nano hello.py
```

Type this:

```python
print("Hello, Robot!")
```

Save it (Ctrl+O, Enter, Ctrl+X).

### Running It

```bash
python3 hello.py
```

You should see:
```
Hello, Robot!
```

**Congratulations!** You just wrote your first Python program!

---

## Comments - Notes for Yourself

Comments are notes in your code. Python ignores them - they're just for you to remember what things do.

```python
# This is a comment - Python ignores this line
print("Hello")  # You can put comments after code too
```

**Use comments to:**
- Explain what your code does
- Remind yourself why you did something
- Help others understand your code

**Example:**
```python
# Start the motor
motor.start()

# Run at 30 RPM for 3 seconds
motor.run(30)
time.sleep(3)

# Stop and clean up
motor.stop()
```

---

## Variables - Storing Information

Variables are like boxes where you store information.

### Creating Variables

```python
speed = 30
name = "Robot"
is_running = True
```

**Rules for variable names:**
- Can use letters, numbers, underscore (_)
- Must start with a letter
- NO spaces (use underscore instead)
- Case matters: `Speed` and `speed` are different!

**Good names:**
```python
motor_speed = 30
robot_name = "Eva"
max_distance = 100
```

**Bad names:**
```python
s = 30              # Too short - what does 's' mean?
motor speed = 30    # NO! Has a space
123speed = 30       # NO! Starts with number
```

### Using Variables

```python
speed = 30
print(speed)        # Prints: 30

motor.run(speed)    # Use variable instead of typing 30
```

### Changing Variables

```python
speed = 30
print(speed)        # Prints: 30

speed = 60          # Change it!
print(speed)        # Prints: 60
```

---

## Numbers and Math

### Types of Numbers

**Integers (whole numbers):**
```python
age = 10
speed = 30
count = 5
```

**Floats (decimal numbers):**
```python
distance = 3.5
temperature = 98.6
pi = 3.14159
```

### Math Operations

```python
# Addition
result = 5 + 3      # result is 8

# Subtraction
result = 10 - 4     # result is 6

# Multiplication
result = 3 * 4      # result is 12

# Division
result = 10 / 2     # result is 5.0 (always gives a float!)

# Integer division (no decimals)
result = 10 // 3    # result is 3

# Remainder (modulo)
result = 10 % 3     # result is 1 (10 ÷ 3 leaves remainder 1)
```

### Using Math with Variables

```python
speed = 30
faster = speed + 10      # faster is 40
slower = speed - 10      # slower is 20
double = speed * 2       # double is 60
half = speed / 2         # half is 15.0
```

**Common robot math:**
```python
# Convert degrees to pulses
degrees = 90
pulses = degrees * 8.889    # pulses is 800.01

# Convert RPM to rotations per second
rpm = 60
rps = rpm / 60              # rps is 1.0

# Calculate total distance
distance_per_rotation = 0.25  # meters
rotations = 4
total_distance = distance_per_rotation * rotations  # 1.0 meter
```

---

## Printing - Showing Information

### Basic Printing

```python
print("Hello")                    # Prints: Hello
print(42)                         # Prints: 42
print(3.14)                       # Prints: 3.14
```

### Printing Variables

```python
speed = 30
print(speed)                      # Prints: 30

name = "Robot"
print(name)                       # Prints: Robot
```

### Printing Multiple Things

```python
speed = 30
print("Speed:", speed)            # Prints: Speed: 30
print("Speed is", speed, "RPM")   # Prints: Speed is 30 RPM
```

### F-Strings (Modern Way)

This is the BEST way to print variables:

```python
speed = 30
print(f"Speed: {speed} RPM")      # Prints: Speed: 30 RPM

name = "Eva"
age = 10
print(f"{name} is {age} years old")  # Prints: Eva is 10 years old
```

**Why f-strings are awesome:**
- Easy to read
- Put variables right where they belong
- Can do math inside them

```python
speed = 30
print(f"Double speed: {speed * 2}")  # Prints: Double speed: 60
```

### Formatting Numbers

```python
# Show 2 decimal places
distance = 3.14159
print(f"Distance: {distance:.2f} meters")  # Prints: Distance: 3.14 meters

# Show as integer (no decimals)
value = 123.456
print(f"Value: {value:.0f}")      # Prints: Value: 123
```

---

## Indentation - SUPER IMPORTANT!

Python uses **indentation** (spaces at the start of lines) to group code. This is VERY important and trips up many beginners!

### What is Indentation?

```python
# No indentation - this is regular code
print("Start")

# Indented code - this belongs to something
    print("This is indented")
```

### When to Indent

You indent code that belongs "inside" something:

```python
# If statement
if speed > 50:
    print("Too fast!")      # Indented - belongs to 'if'
    speed = 50              # Indented - belongs to 'if'

# Loop
for i in range(3):
    print(i)                # Indented - belongs to 'for'
    motor.run(30)           # Indented - belongs to 'for'

# Function
def start_motor():
    motor.start()           # Indented - belongs to function
    motor.run(30)           # Indented - belongs to function
```

### How Much to Indent?

**Use 4 spaces** (or one Tab key). Pick one and stick with it!

```python
# Good (4 spaces)
if speed > 50:
    print("Fast")

# Good (1 tab)
if speed > 50:
	print("Fast")

# BAD (mixing spaces and tabs)
if speed > 50:
    print("Line 1")      # 4 spaces
	print("Line 2")      # 1 tab
# Python will give an error!
```

### Common Indentation Mistakes

**Mistake 1: Forgetting to indent**
```python
# WRONG
if speed > 50:
print("Too fast")        # ERROR! Needs indentation

# CORRECT
if speed > 50:
    print("Too fast")    # Indented!
```

**Mistake 2: Extra indentation**
```python
# WRONG
print("Start")
    print("Next")        # ERROR! Why is this indented?

# CORRECT
print("Start")
print("Next")            # No indent needed
```

**Mistake 3: Inconsistent indentation**
```python
# WRONG
if speed > 50:
    print("Line 1")      # 4 spaces
      print("Line 2")    # 6 spaces - ERROR!

# CORRECT
if speed > 50:
    print("Line 1")      # 4 spaces
    print("Line 2")      # 4 spaces
```

---

## If Statements - Making Decisions

If statements let your program make decisions.

### Basic If

```python
speed = 60

if speed > 50:
    print("Going fast!")
```

This checks: "Is speed greater than 50?" If yes, print the message.

### If-Else

```python
speed = 30

if speed > 50:
    print("Going fast!")
else:
    print("Going slow")
```

If speed is more than 50, print "Going fast!". Otherwise, print "Going slow".

### If-Elif-Else

```python
speed = 45

if speed > 60:
    print("Very fast!")
elif speed > 30:
    print("Medium speed")
else:
    print("Slow")
```

**How it works:**
1. Check if speed > 60 → No? Try next...
2. Check if speed > 30 → Yes! Print "Medium speed" and stop
3. If nothing matched, do else

### Comparison Operators

```python
speed = 50

# Equal to
if speed == 50:
    print("Exactly 50!")

# Not equal to
if speed != 30:
    print("Not 30")

# Greater than
if speed > 40:
    print("More than 40")

# Less than
if speed < 60:
    print("Less than 60")

# Greater than or equal to
if speed >= 50:
    print("50 or more")

# Less than or equal to
if speed <= 50:
    print("50 or less")
```

**Common mistake:**
```python
# WRONG - uses single =
if speed = 50:          # ERROR!

# CORRECT - uses double ==
if speed == 50:         # Checking if equal
```

### Combining Conditions

```python
speed = 40
distance = 100

# AND - both must be true
if speed > 30 and distance > 50:
    print("Fast and far!")

# OR - at least one must be true
if speed > 60 or distance > 200:
    print("Either fast or very far!")

# NOT - opposite
if not speed > 50:
    print("Not going fast")
```

### Robot Examples

```python
# Check if motor has moved
position = motor.get_position()
if position > 3200:
    print("Motor moved more than 1 rotation!")

# Safety check
if speed > 100:
    print("Warning: Speed too high!")
    speed = 100

# Check multiple motors
if motor1.get_position() > 1000 and motor2.get_position() > 1000:
    print("Both motors have moved!")
```

---

## Loops - Repeating Things

Loops let you repeat code multiple times.

### For Loop with Range

Repeat something a specific number of times:

```python
# Print numbers 0 to 4
for i in range(5):
    print(i)

# Output:
# 0
# 1
# 2
# 3
# 4
```

**How range() works:**
```python
range(5)        # 0, 1, 2, 3, 4 (5 numbers starting at 0)
range(1, 6)     # 1, 2, 3, 4, 5 (start at 1, stop before 6)
range(0, 10, 2) # 0, 2, 4, 6, 8 (start at 0, stop before 10, step by 2)
```

**Examples:**
```python
# Count to 10
for i in range(1, 11):
    print(i)

# Count by 10s
for i in range(10, 101, 10):
    print(i)         # Prints: 10, 20, 30, ... 100

# Countdown
for i in range(5, 0, -1):
    print(i)         # Prints: 5, 4, 3, 2, 1
```

### For Loop with Lists

Loop through items in a list:

```python
motors = [motor1, motor2, motor3]

for motor in motors:
    motor.start()
```

**More examples:**
```python
# Loop through numbers
speeds = [10, 20, 30, 40]
for speed in speeds:
    print(f"Speed: {speed}")

# Loop through names
names = ["Eva", "Wall-E", "BB-8"]
for name in names:
    print(f"Hello, {name}!")
```

### While Loop

Repeat while a condition is true:

```python
count = 0

while count < 5:
    print(count)
    count = count + 1

# Output: 0, 1, 2, 3, 4
```

**Robot example:**
```python
# Keep moving until we've gone 10000 pulses
while motor.get_position() < 10000:
    motor.run(30)
    time.sleep(0.1)
motor.stop()
```

**Warning:** Be careful with while loops! If the condition never becomes False, the loop runs forever!

```python
# BAD - runs forever!
while True:
    print("Never stops!")

# GOOD - has a way to stop
count = 0
while count < 10:
    print(count)
    count = count + 1  # This will eventually make count >= 10
```

### Break and Continue

**Break** - exit the loop immediately:
```python
for i in range(100):
    if i == 5:
        break        # Stop loop when i is 5
    print(i)

# Output: 0, 1, 2, 3, 4
```

**Continue** - skip to next iteration:
```python
for i in range(5):
    if i == 2:
        continue     # Skip when i is 2
    print(i)

# Output: 0, 1, 3, 4 (skipped 2)
```

### Robot Examples

```python
# Speed up gradually
for speed in range(10, 101, 10):
    motor.run(speed)
    time.sleep(1)

# Start all motors
motors = [motor1, motor2, motor3, motor4]
for motor in motors:
    motor.start()

# Repeat movement 5 times
for i in range(5):
    motor.run(30)
    time.sleep(2)
    motor.hold()
    time.sleep(1)
```

---

## Functions - Reusing Code

Functions are reusable pieces of code. Instead of writing the same code over and over, write it once in a function!

### Creating a Function

```python
def say_hello():
    print("Hello!")
    print("Nice to meet you!")

# Use the function
say_hello()
say_hello()

# Output:
# Hello!
# Nice to meet you!
# Hello!
# Nice to meet you!
```

**Parts of a function:**
```python
def function_name():    # def, name, (), and :
    # Indented code
    print("Inside function")
```

### Functions with Parameters

Parameters let you give information to the function:

```python
def greet(name):
    print(f"Hello, {name}!")

greet("Eva")       # Prints: Hello, Eva!
greet("Robot")     # Prints: Hello, Robot!
```

**Multiple parameters:**
```python
def run_motor(speed, duration):
    motor.run(speed)
    time.sleep(duration)
    motor.stop()

# Use it
run_motor(30, 3)    # Run at 30 RPM for 3 seconds
run_motor(60, 5)    # Run at 60 RPM for 5 seconds
```

### Functions that Return Values

Functions can give back a result:

```python
def add(a, b):
    result = a + b
    return result

total = add(5, 3)
print(total)        # Prints: 8
```

**Robot examples:**
```python
def pulses_to_degrees(pulses):
    degrees = pulses / 8.889
    return degrees

position = motor.get_position()
degrees = pulses_to_degrees(position)
print(f"Motor at {degrees:.1f} degrees")


def is_motor_moving(motor):
    speed = motor.get_speed()
    if speed != 0:
        return True
    else:
        return False

if is_motor_moving(motor1):
    print("Motor 1 is moving!")
```

### Why Use Functions?

**1. Avoid repetition:**
```python
# Without function - lots of repetition
motor1.start()
motor1.run(30)
time.sleep(2)
motor1.stop()

motor2.start()
motor2.run(30)
time.sleep(2)
motor2.stop()

# With function - write once, use many times
def test_motor(motor):
    motor.start()
    motor.run(30)
    time.sleep(2)
    motor.stop()

test_motor(motor1)
test_motor(motor2)
```

**2. Make code readable:**
```python
# Hard to understand
motor.run(30)
time.sleep(2)
motor.run(60)
time.sleep(2)
motor.run(30)
time.sleep(2)
motor.stop()

# Easy to understand
def speed_test():
    motor.run(30)    # Start slow
    time.sleep(2)
    motor.run(60)    # Speed up
    time.sleep(2)
    motor.run(30)    # Slow down
    time.sleep(2)
    motor.stop()

speed_test()
```

**3. Organize complex code:**
```python
def setup_robot():
    motor1.start()
    motor2.start()
    motor3.start()
    motor4.start()

def drive_forward():
    motor1.run(40)
    motor2.run(40)
    motor3.run(40)
    motor4.run(40)

def stop_robot():
    motor1.stop()
    motor2.stop()
    motor3.stop()
    motor4.stop()

# Main program - very clear!
setup_robot()
drive_forward()
time.sleep(3)
stop_robot()
```

---

## Importing - Using Tools

Import lets you use code that someone else wrote.

### Basic Import

```python
import time

time.sleep(2)    # Use the sleep function from time module
```

### Import from EvaBot

```python
from evabot import Motor

motor = Motor(1)
```

**What this means:**
- `from evabot` - From the evabot package
- `import Motor` - Get the Motor tool

### Common Imports for Robotics

```python
# Always need these
from evabot import Motor
import time

# Create motors
motor1 = Motor(1)

# Use time.sleep()
time.sleep(3)
```

### Import Multiple Things

```python
from evabot import Motor, Robot

motor = Motor(1)
robot = Robot()
```

---

## Time - Waiting and Delays

The `time` module helps you control timing in your programs.

### time.sleep()

Make your program wait:

```python
import time

print("Starting")
time.sleep(2)        # Wait 2 seconds
print("2 seconds later")
```

**Robot usage:**
```python
motor.run(30)
time.sleep(3)        # Let motor run for 3 seconds
motor.stop()
```

**Decimal seconds:**
```python
time.sleep(0.5)      # Wait half a second
time.sleep(0.1)      # Wait 1/10th of a second
time.sleep(2.5)      # Wait 2.5 seconds
```

---

## Putting It All Together

Here's a complete robot program using everything you learned:

```python
# Import tools
from evabot import Motor
import time

# Function to test a motor
def test_motor(motor_id, duration):
    print(f"Testing motor {motor_id}...")

    # Create and start motor
    motor = Motor(motor_id)
    motor.start()

    # Run at different speeds
    speeds = [20, 40, 60, 40, 20]

    for speed in speeds:
        print(f"  Speed: {speed} RPM")
        motor.run(speed)
        time.sleep(duration)

    # Check how far it moved
    position = motor.get_position()
    rotations = position / 3200
    print(f"  Moved {rotations:.2f} rotations")

    # Stop motor
    motor.stop()
    print(f"Motor {motor_id} test complete!\n")

# Main program
print("=== Motor Test Program ===\n")

# Test motors 1 and 2
test_motor(1, 1)
test_motor(2, 1)

print("All tests complete!")
```

**This program uses:**
- ✅ Comments
- ✅ Variables
- ✅ Functions
- ✅ For loops
- ✅ Math
- ✅ F-strings
- ✅ Importing
- ✅ If statements (could add)

---

## Common Beginner Mistakes

### 1. Forgetting Colons

```python
# WRONG
if speed > 50
    print("Fast")

# CORRECT
if speed > 50:
    print("Fast")
```

**Always put `:` after:**
- `if`, `elif`, `else`
- `for`, `while`
- `def function_name()`

### 2. Using = Instead of ==

```python
# WRONG - this assigns 50 to speed
if speed = 50:
    print("Fifty")

# CORRECT - this checks if speed equals 50
if speed == 50:
    print("Fifty")
```

### 3. Wrong Indentation

```python
# WRONG
if speed > 50:
print("Fast")    # Not indented!

# CORRECT
if speed > 50:
    print("Fast")
```

### 4. Misspelled Variable Names

```python
# WRONG
speed = 30
print(Speed)     # Capital S - Python thinks this is different!

# CORRECT
speed = 30
print(speed)     # Same spelling
```

### 5. Forgetting Parentheses

```python
# WRONG
print "Hello"    # Missing ()

# CORRECT
print("Hello")
```

### 6. Division by Zero

```python
# WRONG - causes error!
result = 10 / 0

# CORRECT - check first
if divisor != 0:
    result = 10 / divisor
else:
    print("Can't divide by zero!")
```

---

## Practice Exercises

Try these to practice what you learned!

### Exercise 1: Speed Ramp

Write a program that gradually increases motor speed from 10 to 100 RPM in steps of 10.

<details>
<summary>Solution</summary>

```python
from evabot import Motor
import time

motor = Motor(1)
motor.start()

for speed in range(10, 101, 10):
    print(f"Speed: {speed} RPM")
    motor.run(speed)
    time.sleep(1)

motor.stop()
```
</details>

### Exercise 2: Motor Checker

Write a function that checks if a motor has moved more than 1000 pulses. Print "Moved far!" if yes, "Not far" if no.

<details>
<summary>Solution</summary>

```python
def check_movement(motor):
    position = motor.get_position()
    if position > 1000:
        print("Moved far!")
    else:
        print("Not far")

motor.start()
motor.run(30)
time.sleep(2)
check_movement(motor)
motor.stop()
```
</details>

### Exercise 3: Countdown

Make the motor spin while counting down from 5 to 1, then print "Blast off!" and stop.

<details>
<summary>Solution</summary>

```python
from evabot import Motor
import time

motor = Motor(1)
motor.start()
motor.run(30)

for i in range(5, 0, -1):
    print(i)
    time.sleep(1)

print("Blast off!")
motor.stop()
```
</details>

---

## Quick Reference

### Must Remember

```python
# Import
from evabot import Motor
import time

# Variables
speed = 30
name = "Robot"

# Print
print("Hello")
print(f"Speed: {speed}")

# If statement
if speed > 50:
    print("Fast")
else:
    print("Slow")

# For loop
for i in range(5):
    print(i)

# While loop
count = 0
while count < 5:
    print(count)
    count = count + 1

# Function
def my_function(parameter):
    print(parameter)
    return result

# Comments
# This is a comment
```

### Indentation Rules

- Use 4 spaces (or 1 tab)
- Indent code that belongs "inside" something
- Keep same indentation for code at same level
- Don't mix spaces and tabs!

### Common Symbols

```python
=       # Assign (speed = 30)
==      # Check if equal (if speed == 30)
!=      # Not equal (if speed != 30)
>       # Greater than
<       # Less than
>=      # Greater or equal
<=      # Less or equal
+       # Add
-       # Subtract
*       # Multiply
/       # Divide
#       # Comment
:       # Start a block (if/for/def)
()      # Function call or parameters
[]      # List
```

---

## Next Steps

Now that you know Python basics, you're ready to program robots!

**Go to:** [Chapter 1: Getting Started](chapter1_getting_started.md)

You'll use everything you learned here:
- Variables to store motor speeds
- If statements to make decisions
- Loops to repeat movements
- Functions to organize your code
- Imports to use the Motor class

Have fun programming your robot!
