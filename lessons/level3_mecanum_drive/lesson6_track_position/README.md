# Lesson 3.6: Track Position

**Level**: 3 - Mecanum Drive
**Time**: 60-90 minutes
**Difficulty**: ⭐⭐⭐ Advanced

## What You'll Learn

- Use odometry to track position
- Read robot pose (x, y, theta)
- Monitor velocity
- Understand coordinate systems

## Hardware Needed

- 4× Servo42D motors with mecanum wheels
- CAN interface (can0)
- Motors: FL=4, FR=2, BL=3, BR=1

## Concepts

- Odometry (position tracking)
- Robot pose (x, y, theta)
- Velocity feedback
- Coordinate frames

## What is Odometry?

**Odometry** = tracking position by measuring wheel rotation

Like a car's odometer, but tracks:
- **x**: forward/backward position (meters)
- **y**: left/right position (meters)
- **theta**: rotation angle (radians)

## Coordinate System

```
        Y (left)
        ↑
        |
        |
        +----→ X (forward)
       /
      /
     ↙ Theta (rotation)
  Robot
```

- X-axis: forward (positive) / backward (negative)
- Y-axis: left (positive) / right (negative)
- Theta: CCW rotation from start orientation

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch position being tracked!**

## What Should Happen

1. Robot shows starting position (0, 0, 0)
2. Robot drives forward, position updates (x increases)
3. Robot strafes left, position updates (y increases)
4. Robot rotates, angle updates (theta increases)
5. Program displays final position

## Success Criteria

- ✅ Starting position near (0, 0, 0)
- ✅ Forward motion increases x
- ✅ Left strafe increases y
- ✅ CCW rotation increases theta
- ✅ Position updates in real-time
- ✅ Final position makes sense

## Important Concepts

**Pose**:
- Complete position and orientation
- Format: Pose(x=0.5, y=0.3, theta=0.785)
- Units: x/y in meters, theta in radians

**Velocity**:
- Current speed in x, y, theta
- Derived from wheel speeds
- Updates at 50 Hz

**Odometry Drift**:
- Position becomes less accurate over time
- Wheel slip causes errors
- Normal and expected!
- Later: sensors fix this (IMU, cameras, etc.)

## Common Mistakes

**Problem**: "Position doesn't update"
**Fix**: Odometry thread runs automatically. Check robot.start() was called.

**Problem**: "Position way off after movement"
**Fix**: Normal odometry drift. Wheel slip, surface friction, calibration needed.

**Problem**: "Theta in weird numbers"
**Fix**: Theta in radians. π = 180°, 2π = 360°

## Try These Challenges

After completing the basic lesson:

1. **Target Position**: Drive to exactly (1.0, 0.5, 0) by monitoring odometry
2. **Return Home**: Drive somewhere, then navigate back to (0, 0, 0)
3. **Position Logger**: Save position every second to a file
4. **Drift Test**: Drive 5m forward, measure actual distance vs odometry

## Understanding Drift

Example odometry drift:
```
Commanded: 5.0m forward
Odometry: 4.8m
Actual: 4.6m

Odometry error: 4.8 - 4.6 = 0.2m (4%)
Command error: 5.0 - 4.6 = 0.4m (8%)
```

Odometry is more accurate than open-loop!

## Math Exercise

**Problem**: Robot at (1.0, 0.5, π/4), drives forward 0.5m

Starting pose:
- x = 1.0m
- y = 0.5m
- theta = π/4 = 45°

Forward in robot frame = 0.5m
In world frame:
- Δx = 0.5 × cos(45°) = 0.35m
- Δy = 0.5 × sin(45°) = 0.35m

Final pose:
- x = 1.0 + 0.35 = 1.35m
- y = 0.5 + 0.35 = 0.85m
- theta = 45° (unchanged)

## Next Steps

**Congratulations!** You've completed Level 3!

Next levels (coming soon):
- **Level 4**: Timed Motion - Drive for exact times and distances
- **Level 5**: Sensors - Add sensors (distance, IMU)
- **Level 6**: Navigation - Go to target positions
- **Level 7**: Autonomy - Obstacle avoidance, path planning

---

**Need help?** Check `solution.py` to see how it's done!
