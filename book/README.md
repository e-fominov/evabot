# EvaBot Learning Guide

**From Zero to Autonomous Robot**

Welcome to the EvaBot learning guide! This book will teach you robotics programming step-by-step, starting from controlling a single motor all the way to building autonomous robots with sensors and behaviors.

## What You'll Learn

This guide takes a progressive approach to robotics:

1. **Motor Control** - Start with a single motor, learn the fundamentals
2. **Multi-Motor Systems** - Coordinate multiple motors working together
3. **Drive Systems** - Build mecanum drive for omnidirectional movement
4. **Sensors** - Add lidar and cameras for perception
5. **Autonomous Behavior** - Create robots that think and act on their own
6. **Navigation** - SLAM, mapping, and path planning

## How This Book Works

Each chapter builds on the previous ones:

- **Theory sections** - Brief explanations of concepts (coordinate systems, kinematics, etc.)
- **Hands-on lessons** - Practical coding exercises with real hardware
- **Code examples** - Working solutions you can run immediately
- **Reference guide** - Complete API documentation for all functions

## Prerequisites

- **No programming experience needed!** Start with Python Basics chapter below
- EvaBot hardware setup complete
- `robot` command configured and tested

## Chapter Overview

### 📚 Python Basics (Optional but Recommended)
**Status:** Complete

New to programming? Start here!

Learn just enough Python for robotics:
- Variables and math
- Printing and formatting
- If statements (making decisions)
- Loops (repeating things)
- Functions (reusing code)
- **Special focus:** Indentation (the #1 beginner problem!)

**Time:** 1-2 hours

👉 **[Start here: Python Basics](python_basics.md)**

---

### ✅ Chapter 1: Getting Started
**Status:** Complete

Learn the basics:
- Install EvaBot and connect to your robot
- Your first motor program
- Understanding `robot` commands
- Safety features and troubleshooting

**Time:** 30-45 minutes

---

### ✅ Chapter 2: Motor Control
**Status:** Complete

Master single motor control:
- **Lesson 1.1:** Make it spin
- **Lesson 1.2:** Control speed (forward, backward, speed changes)
- **Lesson 1.3:** Start and stop (hold, disable, stop)
- **Lesson 1.4:** Read position (encoder feedback)
- **Lesson 1.5:** Move exact distances (position control)

**Time:** 2-3 hours

---

### ✅ Chapter 3: Multiple Motors
**Status:** Complete

Control multiple motors together:
- **Lesson 2.1:** Two motors working together
- **Lesson 2.2:** Four motors (full robot!)
- **Lesson 2.3:** Movement patterns (forward, spin, diagonal)

Learn mecanum wheel magic and robot coordination!

**Time:** 2-3 hours

---

### 📋 Chapter 4: Drive Systems
**Status:** Coming Soon

Build a real drive system:
- Mecanum kinematics (how omnidirectional movement works)
- High-level control (move in meters/second instead of RPM)
- Odometry (robot knows where it is!)
- Drive patterns and trajectories
- **Lessons**: 3.1 - 3.6

---

### 📋 Chapter 5: Sensors
**Status:** Planned

Add eyes and ears to your robot:
- RPLidar for obstacle detection
- Orbbec camera for vision
- Sensor data processing
- Sensor fusion

---

### 📋 Chapter 6: Autonomous Behaviors
**Status:** Planned

Make robots think:
- State machines
- Reactive behaviors
- Goal-based planning
- Decision making

---

### 📋 Chapter 7: Navigation & SLAM
**Status:** Planned

Advanced navigation:
- Mapping with lidar
- Localization (knowing where you are)
- Path planning
- Autonomous navigation

## Programming Reference

See [reference.md](reference.md) for complete API documentation including:
- Motor class methods
- MecanumDrive functions
- Sensor interfaces
- Behavior system

## Getting Help

- Check the [reference.md](reference.md) for function documentation
- Review lesson code in the `lessons/` directory
- Create issues at https://github.com/e-fominov/evabot/issues

## How to Use This Book

**Sequential Learning:**
```bash
# Work through chapters in order
cat book/chapter1_getting_started.md
robot lesson 1.1
cd lesson1_1
robot run template.py
```

**Reference Guide:**
```bash
# Look up specific functions
cat book/reference.md | grep "Motor.run"
```

**Theory Review:**
```bash
# Understand concepts before coding
cat book/chapter4_drive_systems.md  # Read mecanum theory
robot lesson 3.1                     # Try the practical lesson
```

---

Let's get started! → [Chapter 1: Getting Started](chapter1_getting_started.md)
